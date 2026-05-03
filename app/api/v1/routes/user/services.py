from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import get_current_user
from app.api.v1.deps.controllers import get_service_controller
from app.controllers.service_controller import ServiceController
from app.models.user import User
from app.schemas.service import ServiceCreate

router = APIRouter(prefix="/services", tags=["User Services"])


@router.post("", status_code=201)
async def user_create_service_request(
    payload: ServiceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    return await controller.user_create(current_user, payload)


@router.get("")
async def user_list_services(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    """All provider listings plus this user's own service requests."""
    return await controller.user_list(current_user)


@router.get("/{service_id}")
async def user_get_service(
    service_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    """Single service if visible: any provider listing, or a user_request owned by you."""
    return await controller.user_get(current_user, service_id)
