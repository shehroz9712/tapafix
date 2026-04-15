from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.repositories.base import BaseRepository


class RolePermissionRepository(BaseRepository[RolePermission]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RolePermission)

    async def list_permission_names_for_role(self, role_id: int) -> list[str]:
        stmt = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def replace_role_permissions(
        self, role_id: int, permission_ids: list[int]
    ) -> None:
        await self.session.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        for pid in permission_ids:
            self.session.add(RolePermission(role_id=role_id, permission_id=pid))
        await self.session.flush()
