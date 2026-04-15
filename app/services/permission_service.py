from sqlalchemy.ext.asyncio import AsyncSession

from app.models import login_as as login_as_const
from app.models.user import User
from app.repositories.role_permission_repository import RolePermissionRepository


class PermissionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_permissions = RolePermissionRepository(session)

    async def permission_names_for_role(self, role_id: int | None) -> list[str]:
        if role_id is None:
            return []
        return await self.role_permissions.list_permission_names_for_role(role_id)

    async def user_has_permission(
        self,
        *,
        user: User,
        permission_name: str,
        jwt_permissions: list[str] | None,
    ) -> bool:
        if user.login_as != login_as_const.ADMIN:
            return False
        if permission_name in (jwt_permissions or []):
            return True
        if user.role_id is None:
            return False
        db_names = await self.permission_names_for_role(user.role_id)
        return permission_name in db_names
