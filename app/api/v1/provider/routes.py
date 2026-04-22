from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import get_current_user, require_provider
from app.api.v1.deps.controllers import (
    get_provider_profile_controller,
    get_vendor_controller,
)
from app.controllers.provider_profile_controller import ProviderProfileController
from app.controllers.vendor_controller import VendorController
from app.models.user import User
from app.schemas.provider_profile import ProviderProfileCreate, ProviderProfilePatch

router = APIRouter(dependencies=[require_provider()])


@router.get("/dashboard")
async def provider_dashboard(
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[VendorController, Depends(get_vendor_controller)],
):
    return await controller.dashboard(provider)


@router.get("/profile")
async def get_provider_profile(
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    return await controller.get_mine(provider)


@router.post("/profile", status_code=201)
async def create_provider_profile(
    payload: ProviderProfileCreate,
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    return await controller.create_profile(provider, payload)


@router.patch("/profile")
async def update_provider_profile(
    payload: ProviderProfilePatch,
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    return await controller.update_profile(provider, payload)
