from __future__ import annotations

from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.schemas.package import PackageCreate, PackageUpdate
from app.services.package_service import PackageService


class PackageController(BaseController):
    def __init__(self, service: PackageService):
        self._service = service

    async def create(self, payload: PackageCreate) -> JSONResponse:
        package = await self._service.create(payload)
        return self.respond_success(self._service.serialize(package), "Package created", 201)

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: str,
    ) -> JSONResponse:
        rows = await self._service.get_all(
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )
        data = [self._service.serialize(row) for row in rows]
        return self.respond_success(data, "Packages retrieved")

    async def get_by_id(self, package_id: int) -> JSONResponse:
        package = await self._service.get_by_id(package_id)
        return self.respond_success(self._service.serialize(package), "Package retrieved")

    async def update(self, package_id: int, payload: PackageUpdate) -> JSONResponse:
        package = await self._service.update(package_id, payload)
        return self.respond_success(self._service.serialize(package), "Package updated")

    async def delete(self, package_id: int) -> JSONResponse:
        await self._service.delete(package_id)
        return self.respond_success(None, "Package deleted")

    async def create_checkout(
        self,
        current_user: User,
        package_id: int,
    ) -> JSONResponse:
        data = await self._service.create_checkout(current_user, package_id)
        return self.respond_success(data, "Checkout session created", 201)

    async def stripe_webhook(self, payload: bytes, stripe_signature: str | None) -> JSONResponse:
        await self._service.handle_stripe_webhook(payload, stripe_signature)
        return self.respond_success({"received": True}, "Webhook processed")

    async def get_all_transactions(
        self,
        *,
        limit: int,
        offset: int,
        user_id: int | None,
        status: str | None,
        sort_order: str,
    ) -> JSONResponse:
        rows = await self._service.get_all_transactions(
            limit=limit,
            offset=offset,
            user_id=user_id,
            status=status,
            sort_order=sort_order,
        )
        data = [self._service.serialize_transaction(row) for row in rows]
        return self.respond_success(data, "Transactions retrieved")

    async def get_transaction_by_id(self, transaction_id: int) -> JSONResponse:
        transaction = await self._service.get_transaction_by_id(transaction_id)
        return self.respond_success(
            self._service.serialize_transaction(transaction),
            "Transaction retrieved",
        )

    async def get_user_transaction_by_id(
        self,
        transaction_id: int,
        current_user: User,
    ) -> JSONResponse:
        transaction = await self._service.get_user_transaction_by_id(
            transaction_id,
            current_user.id,
        )
        return self.respond_success(
            self._service.serialize_transaction(transaction),
            "Transaction retrieved",
        )
