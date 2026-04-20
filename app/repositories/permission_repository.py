from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Permission)

    async def list_permissions(self) -> list[Permission]:
        stmt = select(Permission).order_by(Permission.module, Permission.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Permission | None:
        stmt = select(Permission).where(Permission.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: list[int]) -> list[Permission]:
        if not ids:
            return []
        stmt = select(Permission).where(Permission.id.in_(ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
