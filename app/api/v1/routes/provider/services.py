from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import get_current_user
from app.api.v1.deps.controllers import get_service_controller
from app.controllers.service_controller import ServiceController
from app.models.user import User
from app.schemas.service import ServiceCreate

router = APIRouter(prefix="/services", tags=["Provider Services"])


@router.post("", status_code=201)
async def provider_create_service(
    payload: ServiceCreate,
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    return await controller.provider_create(provider, payload)


@router.get("")
async def provider_list_services(
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    return await controller.provider_list(provider)
