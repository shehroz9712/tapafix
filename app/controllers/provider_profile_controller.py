from __future__ import annotations

from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.schemas.provider_profile import (
    ProviderListingVerificationUpdate,
    ProviderProfileCreate,
    ProviderProfileOut,
    ProviderProfilePatch,
    ProviderSearchItem,
    ProviderSearchQuery,
)
from app.services.provider_profile_service import ProviderProfileService


class ProviderProfileController(BaseController):
    def __init__(self, service: ProviderProfileService):
        self._service = service

    async def get_mine(self, user: User) -> JSONResponse:
        profile = await self._service.get_own_profile(user)
        out = ProviderProfileOut.from_profile_and_user(profile, user)
        return self.respond_success(out.model_dump(), "Provider profile")

    async def create_profile(self, user: User, payload: ProviderProfileCreate) -> JSONResponse:
        profile = await self._service.create_or_replace(user, payload)
        out = ProviderProfileOut.from_profile_and_user(profile, user, otp_verified=True)
        return self.respond_success(out.model_dump(), "Provider profile saved", status_code=201)

    async def update_profile(self, user: User, payload: ProviderProfilePatch) -> JSONResponse:
        profile = await self._service.patch(user, payload)
        out = ProviderProfileOut.from_profile_and_user(profile, user)
        return self.respond_success(out.model_dump(), "Provider profile updated")

    async def get_public(self, user_id: int) -> JSONResponse:
        profile, user = await self._service.get_public_profile(user_id)
        out = ProviderProfileOut.from_profile_and_user(profile, user)
        return self.respond_success(
            out.model_dump(exclude={"cnic_front", "cnic_back"}),
            "Provider profile",
        )

    async def search_public(self, query: ProviderSearchQuery) -> JSONResponse:
        rows = await self._service.search_public(
            latitude=query.latitude,
            longitude=query.longitude,
            category_id=query.category_id,
            subcategory_id=query.subcategory_id,
            skip=query.skip,
            limit=query.limit,
        )
        items = [
            ProviderSearchItem(
                **ProviderProfileOut.from_profile_and_user(p, u).model_dump(
                    exclude={"cnic_front", "cnic_back"}
                ),
                distance_km=dkm,
            ).model_dump()
            for p, u, dkm in rows
        ]
        return self.respond_success({"items": items, "count": len(items)}, "Providers")

    async def admin_set_listing_verified(
        self,
        target_user_id: int,
        payload: ProviderListingVerificationUpdate,
    ) -> JSONResponse:
        profile, user = await self._service.admin_set_listing_verified(
            target_user_id=target_user_id,
            payload=payload,
        )
        out = ProviderProfileOut.from_profile_and_user(profile, user)
        return self.respond_success(out.model_dump(), "Provider listing verification updated")
