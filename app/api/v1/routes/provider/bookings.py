from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.api.v1.deps.auth import get_current_user
from app.api.v1.deps.controllers import get_booking_controller
from app.controllers.booking_controller import BookingController
from app.models.user import User
from app.schemas.booking import BookingRequestCreate

router = APIRouter(prefix="/bookings", tags=["Provider Bookings"])


@router.get("")
async def provider_list_bookings(
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    return await controller.provider_list(provider)


@router.post("/{booking_id}/request", status_code=201)
async def provider_submit_booking_request(
    booking_id: int,
    provider: Annotated[User, Depends(get_current_user)],
    controller: Annotated[BookingController, Depends(get_booking_controller)],
    payload: Annotated[BookingRequestCreate | None, Body()] = None,
):
    body = payload or BookingRequestCreate()
    return await controller.provider_submit_request(provider, booking_id, body)
