from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.schemas.rbac import RoleAssignPermissions, RoleCreate
from app.services.role_service import RoleService


class RoleController(BaseController):
    def __init__(self, service: RoleService):
        self._service = service

    async def create_role(self, payload: RoleCreate) -> JSONResponse:
        role = await self._service.create_role(
            name=payload.name,
            description=payload.description,
            allows_self_registration=payload.allows_self_registration,
        )
        data = self._service.serialize_role_summary(role)
        return self.respond_success(data, "Role created")

    async def list_roles(self) -> JSONResponse:
        roles = await self._service.list_roles()
        data = [self._service.serialize_role_summary(r) for r in roles]
        return self.respond_success(data, "Roles retrieved")

    async def list_permissions(self) -> JSONResponse:
        perms = await self._service.list_permissions()
        data = [self._service.serialize_permission_row(p) for p in perms]
        return self.respond_success(data, "Permissions retrieved")

    async def assign_permissions(
        self, role_id: int, payload: RoleAssignPermissions
    ) -> JSONResponse:
        role = await self._service.assign_permissions_to_role(
            role_id=role_id, permission_ids=payload.permission_ids
        )
        data = self._service.serialize_role_detail(role)
        return self.respond_success(data, "Role permissions updated")
