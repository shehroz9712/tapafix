from __future__ import annotations

from typing import Any

from sqlalchemy import Float, and_, cast, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import login_as as login_as_const
from app.models.provider_profile import ProviderProfile
from app.models.user import User
from app.repositories.base import BaseRepository
from app.utils.geo import haversine_distance_km_sql


def _provider_listing_filter_clauses(
    *,
    min_rating: float | None,
    min_rating_count: int | None,
    pricing_type: str | None,
    min_price: float | None,
    max_price: float | None,
) -> list[Any]:
    """Extra AND clauses for rating / price filters on provider_profiles."""
    clauses: list[Any] = []
    if min_rating is not None:
        clauses.append(cast(ProviderProfile.average_rating, Float) >= float(min_rating))
    if min_rating_count is not None:
        clauses.append(ProviderProfile.rating_count >= int(min_rating_count))

    pj = cast(ProviderProfile.price_per_job, Float)
    ph = cast(ProviderProfile.price_per_hour, Float)

    if pricing_type == "per_job":
        clauses.append(ProviderProfile.price_per_job.isnot(None))
        if min_price is not None:
            clauses.append(pj >= float(min_price))
        if max_price is not None:
            clauses.append(pj <= float(max_price))
    elif pricing_type == "per_hour":
        clauses.append(ProviderProfile.price_per_hour.isnot(None))
        if min_price is not None:
            clauses.append(ph >= float(min_price))
        if max_price is not None:
            clauses.append(ph <= float(max_price))
    elif min_price is not None or max_price is not None:
        job_parts: list[Any] = [ProviderProfile.price_per_job.isnot(None)]
        if min_price is not None:
            job_parts.append(pj >= float(min_price))
        if max_price is not None:
            job_parts.append(pj <= float(max_price))
        hour_parts: list[Any] = [ProviderProfile.price_per_hour.isnot(None)]
        if min_price is not None:
            hour_parts.append(ph >= float(min_price))
        if max_price is not None:
            hour_parts.append(ph <= float(max_price))
        clauses.append(or_(and_(*job_parts), and_(*hour_parts)))

    return clauses


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
        min_rating: float | None = None,
        min_rating_count: int | None = None,
        pricing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
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

        for clause in _provider_listing_filter_clauses(
            min_rating=min_rating,
            min_rating_count=min_rating_count,
            pricing_type=pricing_type,
            min_price=min_price,
            max_price=max_price,
        ):
            stmt = stmt.where(clause)

        stmt = stmt.order_by(dist.asc()).limit(max_rows)
        result = await self.session.execute(stmt)
        rows = result.all()
        out: list[tuple[ProviderProfile, User, float]] = []
        for profile, user, dkm in rows:
            out.append((profile, user, float(dkm)))
        return out

    async def search_top_rated_candidates(
        self,
        *,
        search_lat: float | None,
        search_lon: float | None,
        category_id: int | None,
        subcategory_id: int | None,
        min_rating: float | None = None,
        min_rating_count: int | None = None,
        pricing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        max_rows: int = 500,
    ) -> list[tuple[ProviderProfile, User, float | None]]:
        """Verified providers ordered by rating; optional geo filter within service radius."""
        base_where = [
            User.login_as == login_as_const.PROVIDER,
            User.is_active.is_(True),
            ProviderProfile.is_listing_verified.is_(True),
            ProviderProfile.latitude.isnot(None),
            ProviderProfile.longitude.isnot(None),
            ProviderProfile.service_radius_km.isnot(None),
            cast(ProviderProfile.service_radius_km, Float) > 0,
            text("JSON_LENGTH(provider_profiles.category_ids) > 0"),
            text("JSON_LENGTH(provider_profiles.available_days) > 0"),
        ]

        if category_id is not None:
            base_where.append(
                text(
                    "JSON_CONTAINS(provider_profiles.category_ids, CAST(:cid AS JSON), '$')"
                ).bindparams(cid=int(category_id))
            )
        if subcategory_id is not None:
            base_where.append(
                text(
                    "JSON_CONTAINS(provider_profiles.subcategory_ids, CAST(:sid AS JSON), '$')"
                ).bindparams(sid=int(subcategory_id))
            )

        base_where.extend(
            _provider_listing_filter_clauses(
                min_rating=min_rating,
                min_rating_count=min_rating_count,
                pricing_type=pricing_type,
                min_price=min_price,
                max_price=max_price,
            )
        )

        if search_lat is not None and search_lon is not None:
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
                    *base_where,
                    dist <= cast(ProviderProfile.service_radius_km, Float),
                )
                .order_by(
                    ProviderProfile.average_rating.desc(),
                    ProviderProfile.rating_count.desc(),
                    dist.asc(),
                )
                .limit(max_rows)
            )
            result = await self.session.execute(stmt)
            out: list[tuple[ProviderProfile, User, float | None]] = []
            for profile, user, dkm in result.all():
                out.append((profile, user, float(dkm)))
            return out

        stmt = (
            select(ProviderProfile, User)
            .join(User, User.id == ProviderProfile.user_id)
            .where(*base_where)
            .order_by(
                ProviderProfile.average_rating.desc(),
                ProviderProfile.rating_count.desc(),
            )
            .limit(max_rows)
        )
        result = await self.session.execute(stmt)
        return [(p, u, None) for p, u in result.all()]
