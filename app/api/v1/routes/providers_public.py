from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.controllers import get_provider_profile_controller
from app.controllers.provider_profile_controller import ProviderProfileController
from app.schemas.provider_profile import ProviderSearchQuery

router = APIRouter()


@router.get("/search")
async def search_providers(
    query: Annotated[ProviderSearchQuery, Depends()],
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    return await controller.search_public(query)


@router.get("/{user_id}")
async def get_public_provider_profile(
    user_id: int,
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    return await controller.get_public(user_id)
