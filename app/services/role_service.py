from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, NotFoundError
from app.models.permission import Permission
from app.models.role import Role
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_permission_repository import RolePermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.rbac import PermissionOut, RoleDetailOut, RoleSummary


class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.roles = RoleRepository(session)
        self.permissions = PermissionRepository(session)
        self.role_permissions = RolePermissionRepository(session)
        self.users = UserRepository(session)

    async def create_role(
        self,
        *,
        name: str,
        description: str | None,
        allows_self_registration: bool = False,
    ) -> Role:
        try:
            role = await self.roles.create_role(
                name=name,
                description=description,
                allows_self_registration=allows_self_registration,
            )
            await self.session.commit()
            await self.session.refresh(role)
            return role
        except IntegrityError:
            await self.session.rollback()
            raise BadRequestError("Role name already exists")

    async def list_roles(self) -> list[Role]:
        return await self.roles.list_roles()

    async def list_permissions(self) -> list[Permission]:
        return await self.permissions.list_permissions()

    async def assign_permissions_to_role(
        self, *, role_id: int, permission_ids: list[int]
    ) -> Role:
        role = await self.roles.get_by_id(role_id)
        if not role:
            raise NotFoundError("Role not found")
        unique_ids = list(dict.fromkeys(permission_ids))
        found = await self.permissions.get_by_ids(unique_ids)
        if len(found) != len(unique_ids):
            raise BadRequestError("One or more permissions are invalid")
        await self.role_permissions.replace_role_permissions(role_id, unique_ids)
        await self.session.commit()
        updated = await self.roles.get_by_id_with_permissions(role_id)
        if not updated:
            raise NotFoundError("Role not found")
        return updated

    async def assign_role_to_user(self, *, user_id: int, role_id: int) -> None:
        role = await self.roles.get_by_id(role_id)
        if not role:
            raise BadRequestError("Invalid role")
        if role.name != "ADMIN":
            raise BadRequestError("Only the ADMIN role can be assigned to users")
        user = await self.users.promote_to_admin(user_id, role_id)
        if not user:
            raise NotFoundError("User not found")
        await self.session.commit()

    @staticmethod
    def serialize_role_summary(role: Role) -> dict:
        return RoleSummary.model_validate(role).model_dump()

    @staticmethod
    def serialize_permission_row(permission: Permission) -> dict:
        return PermissionOut.model_validate(permission).model_dump()

    @staticmethod
    def serialize_role_detail(role: Role) -> dict:
        names = sorted([p.name for p in role.permissions])
        base = RoleSummary.model_validate(role).model_dump()
        merged = {**base, "permissions": names}
        return RoleDetailOut.model_validate(merged).model_dump()
