from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import RequirePermission
from app.api.v1.deps.controllers import get_role_controller
from app.controllers.role_controller import RoleController
from app.schemas.rbac import RoleAssignPermissions, RoleAssignUser, RoleCreate

router = APIRouter(prefix="/rbac", tags=["Admin RBAC"])


@router.post("/roles", dependencies=[RequirePermission("manage_roles")])
async def create_role(
    payload: RoleCreate,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.create_role(payload)


@router.get("/roles", dependencies=[RequirePermission("manage_roles")])
async def list_roles(
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.list_roles()


@router.get("/permissions", dependencies=[RequirePermission("manage_roles")])
async def list_permissions(
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.list_permissions()


@router.post(
    "/roles/{role_id}/permissions",
    dependencies=[RequirePermission("manage_roles")],
)
async def assign_role_permissions(
    role_id: int,
    payload: RoleAssignPermissions,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.assign_permissions(role_id, payload)


@router.post(
    "/users/{user_id}/role",
    dependencies=[RequirePermission("manage_roles")],
)
async def assign_user_role(
    user_id: int,
    payload: RoleAssignUser,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.assign_user_role(user_id=user_id, payload=payload)
