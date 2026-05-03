from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import get_current_user, require_user
from app.api.v1.deps.controllers import get_booking_controller
from app.controllers.booking_controller import BookingController
from app.models.user import User
from app.schemas.booking import BookingCancel, BookingCreate

router = APIRouter(
    dependencies=[require_user()],
    prefix="/bookings",
    tags=["User Bookings"],
)


@router.post("", status_code=201)
async def user_create_booking(
    payload: BookingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    return await controller.user_create(current_user, payload)


@router.get("/accepted")
async def user_list_accepted_bookings(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    """Bookings where you accepted a provider (status ``assigned``)."""
    return await controller.user_list_accepted(current_user)


@router.get("/{booking_id}/requests")
async def user_list_booking_requests(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    return await controller.user_list_requests(current_user, booking_id)


@router.get("/{booking_id}")
async def user_get_booking(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    """Single booking you own, including all provider requests."""
    return await controller.user_get_detail(current_user, booking_id)


@router.post("/{booking_id}/accept/{provider_id}")
async def user_accept_provider(
    booking_id: int,
    provider_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    return await controller.user_accept(current_user, booking_id, provider_id)


@router.post("/{booking_id}/reject/{provider_id}")
async def user_reject_provider(
    booking_id: int,
    provider_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    return await controller.user_reject(current_user, booking_id, provider_id)


@router.post("/{booking_id}/cancel")
async def user_cancel_booking(
    booking_id: int,
    payload: BookingCancel,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    """Cancel your booking (open or assigned) with a reason type and optional note."""
    return await controller.user_cancel(current_user, booking_id, payload)
