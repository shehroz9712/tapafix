from __future__ import annotations

import asyncio

import stripe
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.package import Package
from app.models.package_purchase import PackagePurchase
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.package_purchase_repository import PackagePurchaseRepository
from app.repositories.package_repository import PackageRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.package import (
    PackageCreate,
    PackagePurchaseResponse,
    PackageResponse,
    PackageUpdate,
)
from app.schemas.transaction import TransactionResponse


class PackageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.packages = PackageRepository(session)
        self.purchases = PackagePurchaseRepository(session)
        self.transactions = TransactionRepository(session)
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create(self, payload: PackageCreate) -> Package:
        existing = await self.packages.get_by_name(payload.name)
        if existing:
            raise ConflictError("Package name already exists")
        try:
            package = await self.packages.create(
                name=payload.name,
                sort=payload.sort,
                image=payload.image,
                price=payload.price,
                duration=payload.duration,
                description=payload.description,
                payment_interval=payload.payment_interval,
                currency=payload.currency.lower(),
                services=payload.services,
            )
            await self.session.commit()
            return package
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Package name already exists")

    async def get_by_id(self, package_id: int) -> Package:
        package = await self.packages.get_by_id(package_id)
        if not package:
            raise NotFoundError("Package not found")
        return package

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: str,
    ) -> list[Package]:
        return await self.packages.get_all(
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )

    async def update(self, package_id: int, payload: PackageUpdate) -> Package:
        package = await self.get_by_id(package_id)
        data = payload.model_dump(exclude_unset=True)
        if "currency" in data and data["currency"] is not None:
            data["currency"] = str(data["currency"]).lower()
        if "name" in data:
            existing = await self.packages.get_by_name(data["name"])
            if existing and existing.id != package_id:
                raise ConflictError("Package name already exists")
        try:
            updated = await self.packages.update(package, data=data)
            await self.session.commit()
            return updated
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Package name already exists")

    async def delete(self, package_id: int) -> None:
        package = await self.get_by_id(package_id)
        await self.packages.delete(package)
        await self.session.commit()

    async def create_checkout(self, user: User, package_id: int) -> dict:
        package = await self.get_by_id(package_id)
        if not settings.STRIPE_SECRET_KEY:
            raise BadRequestError("Stripe is not configured")

        amount = float(package.price)
        amount_cents = int(round(amount * 100))
        if amount_cents <= 0:
            raise BadRequestError("Package price is invalid")

        session_obj = await asyncio.to_thread(
            stripe.checkout.Session.create,
            mode="payment",
            payment_method_types=["card"],
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer_email=user.email,
            metadata={
                "user_id": str(user.id),
                "package_id": str(package.id),
                "payment_interval": package.payment_interval or "",
            },
            line_items=[
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": package.currency.lower(),
                        "product_data": {"name": package.name},
                        "unit_amount": amount_cents,
                    },
                }
            ],
        )

        purchase = await self.purchases.create(
            user_id=user.id,
            package_id=package.id,
            payment_interval=package.payment_interval,
            amount=amount,
            currency=package.currency.lower(),
            status="pending",
            stripe_checkout_session_id=session_obj.id,
        )
        transaction = await self.transactions.create(
            user_id=user.id,
            package_purchase_id=purchase.id,
            amount=amount,
            currency=package.currency.lower(),
            status="pending",
            provider="stripe",
            provider_session_id=session_obj.id,
        )
        await self.session.commit()

        return {
            "checkout_url": session_obj.url,
            "checkout_session_id": session_obj.id,
            "purchase": self.serialize_purchase(purchase),
            "transaction": self.serialize_transaction(transaction),
        }

    async def handle_stripe_webhook(self, payload: bytes, stripe_signature: str | None) -> None:
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise BadRequestError("Stripe webhook secret is not configured")
        if not stripe_signature:
            raise BadRequestError("Missing stripe signature")

        try:
            event = await asyncio.to_thread(
                stripe.Webhook.construct_event,
                payload,
                stripe_signature,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except stripe.error.SignatureVerificationError:
            raise BadRequestError("Invalid stripe signature")
        except ValueError:
            raise BadRequestError("Invalid stripe payload")

        event_type = event.get("type")
        if event_type not in {"checkout.session.completed", "checkout.session.expired"}:
            return

        checkout_session = event.get("data", {}).get("object", {})
        checkout_session_id = str(checkout_session.get("id", "")).strip()
        if not checkout_session_id:
            return

        purchase = await self.purchases.get_by_checkout_session_id(checkout_session_id)
        if not purchase:
            return
        transaction = await self.transactions.get_by_provider_session_id(checkout_session_id)

        if event_type == "checkout.session.completed":
            payment_intent = checkout_session.get("payment_intent")
            await self.purchases.update(
                purchase,
                data={
                    "status": "paid",
                    "stripe_payment_intent_id": str(payment_intent) if payment_intent else None,
                },
            )
            if transaction:
                await self.transactions.update(
                    transaction,
                    data={
                        "status": "paid",
                        "provider_payment_id": str(payment_intent) if payment_intent else None,
                    },
                )
        elif event_type == "checkout.session.expired":
            await self.purchases.update(purchase, data={"status": "expired"})
            if transaction:
                await self.transactions.update(transaction, data={"status": "expired"})

        await self.session.commit()

    async def get_all_transactions(
        self,
        *,
        limit: int,
        offset: int,
        user_id: int | None,
        status: str | None,
        sort_order: str,
    ) -> list[Transaction]:
        return await self.transactions.get_all(
            limit=limit,
            offset=offset,
            user_id=user_id,
            status=status,
            sort_order=sort_order,
        )

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        transaction = await self.transactions.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError("Transaction not found")
        return transaction

    async def get_user_transaction_by_id(self, transaction_id: int, user_id: int) -> Transaction:
        transaction = await self.transactions.get_by_id_for_user(transaction_id, user_id)
        if not transaction:
            raise NotFoundError("Transaction not found")
        return transaction

    @staticmethod
    def serialize(package: Package) -> dict:
        return PackageResponse.model_validate(package).model_dump()

    @staticmethod
    def serialize_purchase(purchase: PackagePurchase) -> dict:
        return PackagePurchaseResponse.model_validate(purchase).model_dump()

    @staticmethod
    def serialize_transaction(transaction: Transaction) -> dict:
        return TransactionResponse.model_validate(transaction).model_dump()
