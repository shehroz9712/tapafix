from __future__ import annotations

from sqlalchemy import Float, cast, exists, not_, or_, select, text, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import login_as as login_as_const
from app.models.booking import Booking
from app.models.booking_request import BookingRequest
from app.models.provider_profile import ProviderProfile
from app.models.user import User
from app.repositories.base import BaseRepository
from app.utils.geo import haversine_between_sql

BOOKING_OPEN = "open"
BOOKING_ASSIGNED = "assigned"
BOOKING_CANCELLED = "cancelled"


class BookingRepository(BaseRepository[Booking]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Booking)

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: str,
    ) -> list[Booking]:
        stmt = select(Booking)
        if sort_order == "asc":
            stmt = stmt.order_by(Booking.id.asc(), Booking.created_at.asc())
        else:
            stmt = stmt.order_by(Booking.id.desc(), Booking.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_customer_by_status(
        self,
        *,
        user_id: int,
        status: str,
    ) -> list[Booking]:
        stmt = (
            select(Booking)
            .where(Booking.user_id == user_id, Booking.status == status)
            .order_by(Booking.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_open_eligible_for_provider(
        self,
        provider_user_id: int,
    ) -> list[Booking]:
        """Open bookings this provider can see: taxonomy, verified, distance/broadcast, no existing bid."""
        dist = haversine_between_sql(
            Booking.latitude,
            Booking.longitude,
            ProviderProfile.latitude,
            ProviderProfile.longitude,
        )
        has_bid = exists(
            select(literal(1))
            .select_from(BookingRequest)
            .where(
                BookingRequest.booking_id == Booking.id,
                BookingRequest.provider_id == provider_user_id,
            )
        )
        stmt = (
            select(Booking)
            .select_from(Booking)
            .join(ProviderProfile, ProviderProfile.user_id == provider_user_id)
            .join(User, User.id == ProviderProfile.user_id)
            .where(
                Booking.status == BOOKING_OPEN,
                User.is_active.is_(True),
                User.login_as == login_as_const.PROVIDER,
                ProviderProfile.is_listing_verified.is_(True),
                ProviderProfile.latitude.isnot(None),
                ProviderProfile.longitude.isnot(None),
                ProviderProfile.service_radius_km.isnot(None),
                cast(ProviderProfile.service_radius_km, Float) > 0,
                text(
                    "JSON_CONTAINS(provider_profiles.category_ids, CAST(bookings.category_id AS JSON), '$')"
                ),
                text(
                    "JSON_CONTAINS(provider_profiles.subcategory_ids, CAST(bookings.subcategory_id AS JSON), '$')"
                ),
                or_(
                    Booking.is_broadcast.is_(True),
                    dist <= cast(ProviderProfile.service_radius_km, Float),
                ),
                not_(has_bid),
            )
            .order_by(Booking.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class BookingRequestRepository(BaseRepository[BookingRequest]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BookingRequest)

    async def list_for_booking(self, booking_id: int) -> list[BookingRequest]:
        stmt = (
            select(BookingRequest)
            .where(BookingRequest.booking_id == booking_id)
            .order_by(BookingRequest.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_booking_and_provider(
        self,
        booking_id: int,
        provider_id: int,
    ) -> BookingRequest | None:
        stmt = select(BookingRequest).where(
            BookingRequest.booking_id == booking_id,
            BookingRequest.provider_id == provider_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
