from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models import login_as as login_as_const
from app.models.provider_profile import ProviderProfile
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.repositories.provider_profile_repository import ProviderProfileRepository
from app.repositories.subcategory_repository import SubCategoryRepository
from app.schemas.provider_profile import (
    ProviderListingVerificationUpdate,
    ProviderProfileCreate,
    ProviderProfilePatch,
)
from app.utils.availability import is_listing_complete_for_public, is_within_availability


class ProviderProfileService:
    _SCAN_CAP = 500

    def __init__(self, session: AsyncSession):
        self.session = session
        self.profiles = ProviderProfileRepository(session)
        self.categories = CategoryRepository(session)
        self.subcategories = SubCategoryRepository(session)

    @staticmethod
    def _identity_columns(user: User) -> dict[str, Any]:
        return {
            "name": user.name,
            "email": str(user.email).lower(),
            "phone": user.phone,
        }

    async def ensure_stub_for_provider_user(self, user: User) -> ProviderProfile | None:
        if user.login_as != login_as_const.PROVIDER:
            return None
        existing = await self.profiles.get_by_user_id(user.id)
        if existing:
            return existing
        return await self.profiles.create_stub(
            user_id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
        )

    async def get_own_profile(self, user: User) -> ProviderProfile:
        if user.login_as != login_as_const.PROVIDER:
            raise ForbiddenError("Provider account required")
        profile = await self.profiles.get_by_user_id(user.id)
        if not profile:
            raise NotFoundError("Provider profile not found")
        return profile

    async def create_or_replace(self, user: User, payload: ProviderProfileCreate) -> ProviderProfile:
        if user.login_as != login_as_const.PROVIDER:
            raise ForbiddenError("Provider account required")
        await self._validate_taxonomy(payload.category_ids, payload.subcategory_ids)
        data = {**self._serialize_write(payload), **self._identity_columns(user)}
        existing = await self.profiles.get_by_user_id(user.id)
        if existing:
            return (await self.profiles.update_by_user_id(user.id, data)) or existing
        merged = {"user_id": user.id, **data}
        return await self.profiles.create(obj_in=merged)

    async def patch(self, user: User, payload: ProviderProfilePatch) -> ProviderProfile:
        if user.login_as != login_as_const.PROVIDER:
            raise ForbiddenError("Provider account required")
        patch = payload.model_dump(exclude_unset=True)
        if not patch:
            raise BadRequestError("No fields to update")
        profile = await self.profiles.get_by_user_id(user.id)
        if not profile:
            raise NotFoundError("Provider profile not found")

        merged_categories = patch.get("category_ids", profile.category_ids)
        merged_subcats = patch.get("subcategory_ids", profile.subcategory_ids)
        if "category_ids" in patch or "subcategory_ids" in patch:
            await self._validate_taxonomy(
                list(merged_categories or []),
                list(merged_subcats or []),
            )

        update_data: dict[str, Any] = {}
        if "category_ids" in patch:
            update_data["category_ids"] = patch["category_ids"]
        if "subcategory_ids" in patch:
            update_data["subcategory_ids"] = patch["subcategory_ids"]
        if "years_of_experience" in patch:
            update_data["years_of_experience"] = patch["years_of_experience"]
        if "price_per_job" in patch:
            update_data["price_per_job"] = patch["price_per_job"]
        if "price_per_hour" in patch:
            update_data["price_per_hour"] = patch["price_per_hour"]
        if "city" in patch:
            update_data["city"] = patch["city"]
        if "latitude" in patch:
            update_data["latitude"] = patch["latitude"]
        if "longitude" in patch:
            update_data["longitude"] = patch["longitude"]
        if "service_radius_km" in patch:
            update_data["service_radius_km"] = patch["service_radius_km"]
        if "cnic_front" in patch:
            update_data["cnic_front"] = str(patch["cnic_front"]) if patch["cnic_front"] else None
        if "cnic_back" in patch:
            update_data["cnic_back"] = str(patch["cnic_back"]) if patch["cnic_back"] else None
        if "certificates" in patch and patch["certificates"] is not None:
            update_data["certificates"] = [str(u) for u in patch["certificates"]]
        if "available_days" in patch and patch["available_days"] is not None:
            if not patch["available_days"]:
                raise BadRequestError("available_days cannot be empty when provided")
            update_data["available_days"] = [dict(s) for s in patch["available_days"]]

        update_data.update(self._identity_columns(user))

        updated = await self.profiles.update_by_user_id(user.id, update_data)
        if not updated:
            raise NotFoundError("Provider profile not found")
        return updated

    async def get_public_profile(self, user_id: int) -> tuple[ProviderProfile, User]:
        profile = await self.profiles.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Provider profile not found")
        user = await self.session.get(User, user_id)
        if (
            not user
            or not user.is_active
            or user.login_as != login_as_const.PROVIDER
        ):
            raise NotFoundError("Provider profile not found")
        if not is_listing_complete_for_public(profile):
            raise NotFoundError("Provider profile not found")
        if not is_within_availability(profile.available_days):
            raise NotFoundError("Provider profile not found")
        return profile, user

    async def search_public(
        self,
        *,
        latitude: float,
        longitude: float,
        category_id: int | None,
        subcategory_id: int | None,
        min_rating: float | None = None,
        min_rating_count: int | None = None,
        pricing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        skip: int,
        limit: int,
    ) -> list[tuple[ProviderProfile, User, float]]:
        candidates = await self.profiles.search_public_candidates(
            search_lat=latitude,
            search_lon=longitude,
            category_id=category_id,
            subcategory_id=subcategory_id,
            min_rating=min_rating,
            min_rating_count=min_rating_count,
            pricing_type=pricing_type,
            min_price=min_price,
            max_price=max_price,
            max_rows=self._SCAN_CAP,
        )
        visible: list[tuple[ProviderProfile, User, float]] = []
        for profile, user, dkm in candidates:
            if not is_listing_complete_for_public(profile):
                continue
            if not is_within_availability(profile.available_days):
                continue
            visible.append((profile, user, dkm))
        return visible[skip : skip + limit]

    async def search_top_rated(
        self,
        *,
        latitude: float | None,
        longitude: float | None,
        category_id: int | None,
        subcategory_id: int | None,
        min_rating: float | None = None,
        min_rating_count: int | None = None,
        pricing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        skip: int,
        limit: int,
    ) -> list[tuple[ProviderProfile, User, float | None]]:
        candidates = await self.profiles.search_top_rated_candidates(
            search_lat=latitude,
            search_lon=longitude,
            category_id=category_id,
            subcategory_id=subcategory_id,
            min_rating=min_rating,
            min_rating_count=min_rating_count,
            pricing_type=pricing_type,
            min_price=min_price,
            max_price=max_price,
            max_rows=self._SCAN_CAP,
        )
        visible: list[tuple[ProviderProfile, User, float | None]] = []
        for profile, user, dkm in candidates:
            if not is_listing_complete_for_public(profile):
                continue
            if not is_within_availability(profile.available_days):
                continue
            visible.append((profile, user, dkm))
        return visible[skip : skip + limit]

    async def admin_set_listing_verified(
        self,
        *,
        target_user_id: int,
        payload: ProviderListingVerificationUpdate,
    ) -> tuple[ProviderProfile, User]:
        user = await self.session.get(User, target_user_id)
        if not user or user.login_as != login_as_const.PROVIDER:
            raise BadRequestError("Target user is not a provider")
        profile = await self.profiles.get_by_user_id(target_user_id)
        if not profile:
            raise NotFoundError("Provider profile not found")
        updated = await self.profiles.update_by_user_id(
            target_user_id,
            {"is_listing_verified": payload.is_listing_verified},
        )
        if not updated:
            raise NotFoundError("Provider profile not found")
        return updated, user

    def _serialize_write(self, payload: ProviderProfileCreate) -> dict[str, Any]:
        return {
            "category_ids": list(payload.category_ids),
            "subcategory_ids": list(payload.subcategory_ids),
            "years_of_experience": payload.years_of_experience,
            "price_per_job": payload.price_per_job,
            "price_per_hour": payload.price_per_hour,
            "city": payload.city,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "service_radius_km": payload.service_radius_km,
            "cnic_front": str(payload.cnic_front) if payload.cnic_front else None,
            "cnic_back": str(payload.cnic_back) if payload.cnic_back else None,
            "certificates": [str(u) for u in payload.certificates],
            "available_days": [s.model_dump() for s in payload.available_days],
        }

    async def _validate_taxonomy(self, category_ids: list[int], subcategory_ids: list[int]) -> None:
        if not category_ids:
            raise BadRequestError("category_ids must not be empty")
        n_cat = await self.categories.count_active_by_ids(category_ids)
        if n_cat != len(set(category_ids)):
            raise BadRequestError("One or more category_ids are invalid or inactive")
        if not subcategory_ids:
            raise BadRequestError("subcategory_ids must not be empty")
        rows = await self.subcategories.list_active_by_ids(subcategory_ids)
        if len(rows) != len(set(subcategory_ids)):
            raise BadRequestError("One or more subcategory_ids are invalid or inactive")
        cat_set = set(category_ids)
        for sc in rows:
            if sc.category_id not in cat_set:
                raise BadRequestError(
                    "Each subcategory must belong to one of the selected categories"
                )
