from __future__ import annotations

from typing import Any

from sqlalchemy import Float, cast, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import login_as as login_as_const
from app.models.provider_profile import ProviderProfile
from app.models.user import User
from app.repositories.base import BaseRepository
from app.utils.geo import haversine_distance_km_sql


class ProviderProfileRepository(BaseRepository[ProviderProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ProviderProfile)

    async def get_by_user_id(self, user_id: int) -> ProviderProfile | None:
        stmt = select(ProviderProfile).where(ProviderProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_stub(
        self,
        *,
        user_id: int,
        name: str,
        email: str,
        phone: str | None,
    ) -> ProviderProfile:
        return await self.create(
            obj_in={
                "user_id": user_id,
                "name": name,
                "email": email,
                "phone": phone,
                "category_ids": [],
                "subcategory_ids": [],
                "certificates": [],
                "available_days": [],
                "is_listing_verified": False,
            }
        )

    async def update_by_user_id(self, user_id: int, data: dict[str, Any]) -> ProviderProfile | None:
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None
        await self.update_by_id(profile.id, data)
        return await self.get_by_user_id(user_id)

    async def search_public_candidates(
        self,
        *,
        search_lat: float,
        search_lon: float,
        category_id: int | None,
        subcategory_id: int | None,
        max_rows: int = 500,
    ) -> list[tuple[ProviderProfile, User, float]]:
        """Geo + taxonomy filters in SQL; caller still filters availability in Python."""
        dist = haversine_distance_km_sql(
            ProviderProfile.latitude,
            ProviderProfile.longitude,
            search_lat,
            search_lon,
        ).label("distance_km")

        stmt = (
            select(ProviderProfile, User, dist)
            .join(User, User.id == ProviderProfile.user_id)
            .where(
                User.login_as == login_as_const.PROVIDER,
                User.is_active.is_(True),
                ProviderProfile.is_listing_verified.is_(True),
                ProviderProfile.latitude.isnot(None),
                ProviderProfile.longitude.isnot(None),
                ProviderProfile.service_radius_km.isnot(None),
                cast(ProviderProfile.service_radius_km, Float) > 0,
                text("JSON_LENGTH(provider_profiles.category_ids) > 0"),
                text("JSON_LENGTH(provider_profiles.available_days) > 0"),
                dist <= cast(ProviderProfile.service_radius_km, Float),
            )
        )

        if category_id is not None:
            stmt = stmt.where(
                text(
                    "JSON_CONTAINS(provider_profiles.category_ids, CAST(:cid AS JSON), '$')"
                ).bindparams(cid=int(category_id))
            )
        if subcategory_id is not None:
            stmt = stmt.where(
                text(
                    "JSON_CONTAINS(provider_profiles.subcategory_ids, CAST(:sid AS JSON), '$')"
                ).bindparams(sid=int(subcategory_id))
            )

        stmt = stmt.order_by(dist.asc()).limit(max_rows)
        result = await self.session.execute(stmt)
        rows = result.all()
        out: list[tuple[ProviderProfile, User, float]] = []
        for profile, user, dkm in rows:
            out.append((profile, user, float(dkm)))
        return out
