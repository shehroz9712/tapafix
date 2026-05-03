from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models import login_as as login_as_const
from app.models.booking import Booking
from app.models.booking_request import BookingRequest
from app.models.user import User
from app.repositories.booking_repository import (
    BOOKING_ASSIGNED,
    BOOKING_OPEN,
    BookingRepository,
    BookingRequestRepository,
)
from app.repositories.provider_profile_repository import ProviderProfileRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.subcategory_repository import SubCategoryRepository
from app.schemas.booking import (
    BookingCancel,
    BookingCreate,
    BookingDetailResponse,
    BookingRequestCreate,
    BookingRequestResponse,
    BookingResponse,
)
from app.utils.availability import is_listing_complete_for_public, is_within_availability
from app.utils.geo import haversine_km

REQ_PENDING = "pending"
REQ_ACCEPTED = "accepted"
REQ_REJECTED = "rejected"
REQ_AUTO_CLOSED = "auto_closed"


class BookingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.bookings = BookingRepository(session)
        self.requests = BookingRequestRepository(session)
        self.subcategories = SubCategoryRepository(session)
        self.services = ServiceRepository(session)
        self.profiles = ProviderProfileRepository(session)

    def serialize_booking(self, row: Booking) -> dict:
        data = BookingResponse.model_validate(row).model_dump()
        data["latitude"] = float(data["latitude"])
        data["longitude"] = float(data["longitude"])
        return data

    def serialize_request(self, row: BookingRequest) -> dict:
        return BookingRequestResponse.model_validate(row).model_dump()

    async def _refresh_counts(self, booking: Booking) -> None:
        reqs = await self.requests.list_for_booking(booking.id)
        booking.total_requests = len(reqs)
        booking.pending_count = sum(1 for r in reqs if r.status == REQ_PENDING)
        booking.accepted_count = sum(1 for r in reqs if r.status == REQ_ACCEPTED)
        booking.rejected_count = sum(1 for r in reqs if r.status == REQ_REJECTED)
        booking.auto_closed_count = sum(1 for r in reqs if r.status == REQ_AUTO_CLOSED)
        await self.session.flush()

    async def create_booking(self, user: User, payload: BookingCreate) -> Booking:
        sub = await self.subcategories.get_by_id(payload.subcategory_id)
        if not sub:
            raise BadRequestError("Subcategory not found")
        if sub.category_id != payload.category_id:
            raise BadRequestError("Subcategory does not belong to category")
        svc = await self.services.get_by_id(payload.service_id)
        if not svc:
            raise BadRequestError("Service not found")
        try:
            row = await self.bookings.create(
                obj_in={
                    "user_id": user.id,
                    "category_id": payload.category_id,
                    "subcategory_id": payload.subcategory_id,
                    "service_id": payload.service_id,
                    "scheduled_date": payload.scheduled_date,
                    "start_time": payload.start_time,
                    "end_time": payload.end_time,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "note": (payload.note.strip() or None) if payload.note else None,
                    "is_broadcast": payload.is_broadcast,
                    "status": BOOKING_OPEN,
                    "total_requests": 0,
                    "accepted_count": 0,
                    "rejected_count": 0,
                    "pending_count": 0,
                    "auto_closed_count": 0,
                }
            )
            await self.session.commit()
            await self.session.refresh(row)
            return row
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Could not create booking")

    async def admin_list(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: str,
    ) -> list[Booking]:
        return await self.bookings.get_all(limit=limit, offset=offset, sort_order=sort_order)

    async def admin_get_detail(self, booking_id: int) -> BookingDetailResponse:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        reqs = await self.requests.list_for_booking(booking_id)
        base = BookingDetailResponse.model_validate(booking).model_dump()
        base["latitude"] = float(base["latitude"])
        base["longitude"] = float(base["longitude"])
        base["requests"] = [BookingRequestResponse.model_validate(r).model_dump() for r in reqs]
        return BookingDetailResponse(**base)

    def _taxonomy_distance_ok(self, profile, booking: Booking) -> bool:
        cats = [int(x) for x in (profile.category_ids or []) if x is not None]
        subs = [int(x) for x in (profile.subcategory_ids or []) if x is not None]
        if int(booking.category_id) not in cats:
            return False
        if int(booking.subcategory_id) not in subs:
            return False
        if booking.is_broadcast:
            return True
        if profile.latitude is None or profile.longitude is None:
            return False
        if profile.service_radius_km is None:
            return False
        d_km = haversine_km(
            float(booking.latitude),
            float(booking.longitude),
            float(profile.latitude),
            float(profile.longitude),
        )
        return d_km <= float(profile.service_radius_km)

    async def list_bookings_for_provider(self, provider: User) -> list[Booking]:
        profile = await self.profiles.get_by_user_id(provider.id)
        if not profile or not is_listing_complete_for_public(profile):
            return []
        rows = await self.bookings.list_open_eligible_for_provider(provider.id)
        out: list[Booking] = []
        for b in rows:
            if not self._taxonomy_distance_ok(profile, b):
                continue
            if not is_within_availability(profile.available_days):
                continue
            out.append(b)
        return out

    async def _ensure_provider_can_bid(self, provider: User, booking: Booking) -> None:
        if provider.login_as != login_as_const.PROVIDER:
            raise ForbiddenError("Provider account required")
        profile = await self.profiles.get_by_user_id(provider.id)
        if not profile or not is_listing_complete_for_public(profile):
            raise ForbiddenError("Listing must be complete and verified")
        if not is_within_availability(profile.available_days):
            raise BadRequestError("Outside availability window")
        if booking.status != BOOKING_OPEN:
            raise BadRequestError("Booking is not open")
        if not self._taxonomy_distance_ok(profile, booking):
            raise ForbiddenError("Booking not eligible for your profile")
        existing = await self.requests.get_by_booking_and_provider(booking.id, provider.id)
        if existing:
            raise ConflictError("You already submitted a request for this booking")

    async def provider_submit_request(
        self,
        provider: User,
        booking_id: int,
        payload: BookingRequestCreate,
    ) -> BookingRequest:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        await self._ensure_provider_can_bid(provider, booking)
        try:
            req = await self.requests.create(
                obj_in={
                    "booking_id": booking.id,
                    "provider_id": provider.id,
                    "status": REQ_PENDING,
                    "message": payload.message,
                }
            )
            await self.session.flush()
            await self._refresh_counts(booking)
            await self.session.commit()
            await self.session.refresh(req)
            return req
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Duplicate request")

    async def user_list_requests(self, customer: User, booking_id: int) -> list[BookingRequest]:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if booking.user_id != customer.id:
            raise ForbiddenError("Not your booking")
        return await self.requests.list_for_booking(booking_id)

    async def user_list_accepted(self, customer: User) -> list[Booking]:
        return await self.bookings.list_for_customer_by_status(
            user_id=customer.id,
            status=BOOKING_ASSIGNED,
        )

    async def user_get_booking_detail(self, customer: User, booking_id: int) -> BookingDetailResponse:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if booking.user_id != customer.id:
            raise ForbiddenError("Not your booking")
        reqs = await self.requests.list_for_booking(booking_id)
        base = BookingDetailResponse.model_validate(booking).model_dump()
        base["latitude"] = float(base["latitude"])
        base["longitude"] = float(base["longitude"])
        base["requests"] = [BookingRequestResponse.model_validate(r).model_dump() for r in reqs]
        return BookingDetailResponse(**base)

    async def user_accept_provider(
        self,
        customer: User,
        booking_id: int,
        provider_id: int,
    ) -> Booking:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if booking.user_id != customer.id:
            raise ForbiddenError("Not your booking")
        if booking.status != BOOKING_OPEN:
            raise BadRequestError("Booking is no longer open")

        target = await self.requests.get_by_booking_and_provider(booking_id, provider_id)
        if not target or target.status != REQ_PENDING:
            raise BadRequestError("No pending request from this provider")

        pending_list = [
            r for r in await self.requests.list_for_booking(booking_id) if r.status == REQ_PENDING
        ]
        for r in pending_list:
            if r.id == target.id:
                r.status = REQ_ACCEPTED
            else:
                r.status = REQ_AUTO_CLOSED

        booking.status = BOOKING_ASSIGNED
        await self.session.flush()
        await self._refresh_counts(booking)
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def user_reject_provider(
        self,
        customer: User,
        booking_id: int,
        provider_id: int,
    ) -> BookingRequest:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if booking.user_id != customer.id:
            raise ForbiddenError("Not your booking")
        if booking.status != BOOKING_OPEN:
            raise BadRequestError("Booking is no longer open")

        req_row = await self.requests.get_by_booking_and_provider(booking_id, provider_id)
        if not req_row:
            raise NotFoundError("Request not found")
        if req_row.status != REQ_PENDING:
            raise BadRequestError("Request is not pending")

        req_row.status = REQ_REJECTED
        await self.session.flush()
        await self._refresh_counts(booking)
        await self.session.commit()
        await self.session.refresh(req_row)
        return req_row

    async def user_cancel_booking(
        self,
        customer: User,
        booking_id: int,
        payload: BookingCancel,
    ) -> Booking:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if booking.user_id != customer.id:
            raise ForbiddenError("Not your booking")
        if booking.status == BOOKING_CANCELLED:
            raise BadRequestError("Booking is already cancelled")
        if booking.status not in (BOOKING_OPEN, BOOKING_ASSIGNED):
            raise BadRequestError("Booking cannot be cancelled")

        note = (payload.cancellation_note.strip() or None) if payload.cancellation_note else None
        booking.status = BOOKING_CANCELLED
        booking.cancellation_reason_type = payload.reason_type
        booking.cancellation_note = note
        booking.cancelled_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(booking)
        return booking
