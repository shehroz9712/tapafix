from __future__ import annotations

from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.schemas.booking import BookingCancel, BookingCreate, BookingRequestCreate
from app.schemas.category import SortOrder
from app.services.booking_service import BookingService


class BookingController(BaseController):
    def __init__(self, service: BookingService):
        self._service = service

    async def user_create(self, user: User, payload: BookingCreate) -> JSONResponse:
        row = await self._service.create_booking(user, payload)
        return self.respond_success(self._service.serialize_booking(row), "Booking created", 201)

    async def user_list_requests(self, user: User, booking_id: int) -> JSONResponse:
        rows = await self._service.user_list_requests(user, booking_id)
        data = [self._service.serialize_request(r) for r in rows]
        return self.respond_success(data, "Requests retrieved")

    async def user_list_accepted(self, user: User) -> JSONResponse:
        rows = await self._service.user_list_accepted(user)
        data = [self._service.serialize_booking(r) for r in rows]
        return self.respond_success(data, "Bookings retrieved")

    async def user_get_detail(self, user: User, booking_id: int) -> JSONResponse:
        detail = await self._service.user_get_booking_detail(user, booking_id)
        return self.respond_success(detail.model_dump(), "Booking retrieved")

    async def user_accept(
        self,
        user: User,
        booking_id: int,
        provider_id: int,
    ) -> JSONResponse:
        row = await self._service.user_accept_provider(user, booking_id, provider_id)
        return self.respond_success(self._service.serialize_booking(row), "Provider accepted")

    async def user_reject(
        self,
        user: User,
        booking_id: int,
        provider_id: int,
    ) -> JSONResponse:
        req_row = await self._service.user_reject_provider(user, booking_id, provider_id)
        return self.respond_success(self._service.serialize_request(req_row), "Request rejected")

    async def user_cancel(self, user: User, booking_id: int, payload: BookingCancel) -> JSONResponse:
        row = await self._service.user_cancel_booking(user, booking_id, payload)
        return self.respond_success(self._service.serialize_booking(row), "Booking cancelled")

    async def provider_list(self, provider: User) -> JSONResponse:
        rows = await self._service.list_bookings_for_provider(provider)
        data = [self._service.serialize_booking(r) for r in rows]
        return self.respond_success(data, "Bookings retrieved")

    async def provider_submit_request(
        self,
        provider: User,
        booking_id: int,
        payload: BookingRequestCreate,
    ) -> JSONResponse:
        req_row = await self._service.provider_submit_request(provider, booking_id, payload)
        return self.respond_success(
            self._service.serialize_request(req_row),
            "Request submitted",
            201,
        )

    async def admin_list(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: SortOrder,
    ) -> JSONResponse:
        rows = await self._service.admin_list(
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )
        data = [self._service.serialize_booking(r) for r in rows]
        return self.respond_success(data, "Bookings retrieved")

    async def admin_get_detail(self, booking_id: int) -> JSONResponse:
        detail = await self._service.admin_get_detail(booking_id)
        return self.respond_success(detail.model_dump(), "Booking retrieved")
