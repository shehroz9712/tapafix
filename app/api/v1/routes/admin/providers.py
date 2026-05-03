from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import RequirePermission
from app.api.v1.deps.controllers import get_provider_profile_controller
from app.controllers.provider_profile_controller import ProviderProfileController
from app.schemas.provider_profile import ProviderListingVerificationUpdate

router = APIRouter(prefix="/providers", tags=["Admin Providers"])


@router.patch(
    "/{user_id}/listing-verification",
    dependencies=[RequirePermission("manage_users")],
)
async def admin_provider_listing_verification(
    user_id: int,
    payload: ProviderListingVerificationUpdate,
    controller: Annotated[
        ProviderProfileController, Depends(get_provider_profile_controller)
    ],
):
    return await controller.admin_set_listing_verified(user_id, payload)
