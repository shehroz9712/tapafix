from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def create(
        self,
        *,
        user_id: int,
        package_purchase_id: int,
        amount: float,
        currency: str,
        status: str,
        provider: str,
        provider_session_id: str | None,
    ) -> Transaction:
        return await super().create(
            obj_in={
                "user_id": user_id,
                "package_purchase_id": package_purchase_id,
                "amount": amount,
                "currency": currency,
                "status": status,
                "provider": provider,
                "provider_session_id": provider_session_id,
            }
        )

    async def get_by_provider_session_id(self, provider_session_id: str) -> Transaction | None:
        stmt = select(Transaction).where(Transaction.provider_session_id == provider_session_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, transaction_id: int, user_id: int) -> Transaction | None:
        stmt = select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        user_id: int | None,
        status: str | None,
        sort_order: str,
    ) -> list[Transaction]:
        stmt = select(Transaction)
        if user_id is not None:
            stmt = stmt.where(Transaction.user_id == user_id)
        if status:
            stmt = stmt.where(Transaction.status == status)
        if sort_order == "asc":
            stmt = stmt.order_by(Transaction.created_at.asc())
        else:
            stmt = stmt.order_by(Transaction.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, transaction: Transaction, *, data: dict) -> Transaction:
        for key, value in data.items():
            setattr(transaction, key, value)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction
