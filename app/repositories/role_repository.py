from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Role)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(func.lower(Role.name) == name.strip().lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_roles(self) -> list[Role]:
        stmt = select(Role).order_by(Role.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_with_permissions(self, role_id: int) -> Role | None:
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(joinedload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_role(
        self,
        *,
        name: str,
        description: str | None,
        allows_self_registration: bool = False,
    ) -> Role:
        return await self.create(
            obj_in={
                "name": name.strip().upper(),
                "description": description,
                "allows_self_registration": allows_self_registration,
            }
        )
