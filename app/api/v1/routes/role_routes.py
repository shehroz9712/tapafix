from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import RequirePermission, require_admin
from app.api.v1.deps.controllers import get_role_controller
from app.controllers.role_controller import RoleController
from app.schemas.rbac import RoleAssignPermissions, RoleCreate

router = APIRouter(
    prefix="/rbac",
    dependencies=[require_admin(), RequirePermission("manage_roles")],
)


@router.post("/roles")
async def create_role(
    payload: RoleCreate,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.create_role(payload)


@router.get("/roles")
async def list_roles(
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.list_roles()


@router.get("/permissions")
async def list_permissions(
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.list_permissions()


@router.post("/roles/{role_id}/permissions")
async def assign_role_permissions(
    role_id: int,
    payload: RoleAssignPermissions,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.assign_permissions(role_id, payload)
