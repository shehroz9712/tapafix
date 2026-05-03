from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Service)

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: str,
    ) -> list[Service]:
        stmt = select(Service)
        if sort_order == "asc":
            stmt = stmt.order_by(Service.id.asc(), Service.created_at.asc())
        else:
            stmt = stmt.order_by(Service.id.desc(), Service.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_user_discovery(self, *, user_id: int) -> list[Service]:
        stmt = select(Service).where(
            or_(
                Service.service_kind == "provider_listing",
                (Service.service_kind == "user_request") & (Service.user_id == user_id),
            )
        ).order_by(Service.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_visible_for_user(self, *, user_id: int, service_id: int) -> Service | None:
        stmt = (
            select(Service)
            .where(
                Service.id == service_id,
                or_(
                    Service.service_kind == "provider_listing",
                    (Service.service_kind == "user_request") & (Service.user_id == user_id),
                ),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_provider_listings(self, *, provider_user_id: int) -> list[Service]:
        stmt = (
            select(Service)
            .where(
                Service.user_id == provider_user_id,
                Service.service_kind == "provider_listing",
            )
            .order_by(Service.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, row: Service, *, data: dict) -> Service:
        for key, value in data.items():
            setattr(row, key, value)
        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def delete(self, row: Service) -> None:
        await self.session.delete(row)
        await self.session.flush()
