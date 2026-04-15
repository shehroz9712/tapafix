from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission, get_current_user, require_admin
from app.api.v1.deps.controllers import get_admin_controller
from app.controllers.admin_controller import AdminController
from app.models.user import User

router = APIRouter(
    dependencies=[require_admin(), RequirePermission("manage_users")],
)


@router.get("/users")
async def admin_list_users(
    admin: Annotated[User, Depends(get_current_user)],
    controller: Annotated[AdminController, Depends(get_admin_controller)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await controller.list_users(admin, skip=skip, limit=limit)
