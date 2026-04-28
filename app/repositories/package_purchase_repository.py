from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.package_purchase import PackagePurchase
from app.repositories.base import BaseRepository


class PackagePurchaseRepository(BaseRepository[PackagePurchase]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PackagePurchase)

    async def create(
        self,
        *,
        user_id: int,
        package_id: int,
        payment_interval: str | None,
        amount: float,
        currency: str,
        status: str,
        stripe_checkout_session_id: str | None,
    ) -> PackagePurchase:
        return await super().create(
            obj_in={
                "user_id": user_id,
                "package_id": package_id,
                "payment_interval": payment_interval,
                "amount": amount,
                "currency": currency,
                "status": status,
                "stripe_checkout_session_id": stripe_checkout_session_id,
            }
        )

    async def get_by_checkout_session_id(self, checkout_session_id: str) -> PackagePurchase | None:
        stmt = select(PackagePurchase).where(
            PackagePurchase.stripe_checkout_session_id == checkout_session_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, purchase: PackagePurchase, *, data: dict) -> PackagePurchase:
        for key, value in data.items():
            setattr(purchase, key, value)
        await self.session.flush()
        await self.session.refresh(purchase)
        return purchase
