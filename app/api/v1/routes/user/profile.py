from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import get_current_user
from app.api.v1.deps.controllers import get_user_controller
from app.controllers.user_controller import UserController
from app.models.user import User
from app.schemas.user import UserProfileUpdate

router = APIRouter(prefix="", tags=["User Profile"])


@router.get("/me")
async def read_me(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[UserController, Depends(get_user_controller)],
):
    return await controller.me(current_user)


@router.patch("/me")
async def patch_me(
    payload: UserProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[UserController, Depends(get_user_controller)],
):
    return await controller.update_profile(current_user, payload)
