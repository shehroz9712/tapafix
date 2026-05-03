from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.controllers import get_provider_profile_controller
from app.controllers.provider_profile_controller import ProviderProfileController
from app.schemas.provider_profile import ProviderSearchQuery, WorkerTopRatedQuery

router = APIRouter(prefix="/workers", tags=["User — Workers"])


@router.get("")
async def list_workers_nearby(
    query: Annotated[ProviderSearchQuery, Depends()],
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    """List verified workers in range (same rules as public provider search)."""
    return await controller.search_public(query)


@router.get("/top-rated")
async def list_top_rated_workers(
    query: Annotated[WorkerTopRatedQuery, Depends()],
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    """Top-rated workers; optional latitude/longitude to restrict to those in service radius."""
    return await controller.search_top_rated(query)


@router.get("/{user_id}")
async def get_worker_profile(
    user_id: int,
    controller: Annotated[ProviderProfileController, Depends(get_provider_profile_controller)],
):
    """Single public worker (provider) profile by user id."""
    return await controller.get_public(user_id)
