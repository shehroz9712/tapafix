from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission
from app.api.v1.deps.controllers import get_booking_controller
from app.controllers.booking_controller import BookingController
from app.schemas.category import SortOrder

router = APIRouter(prefix="/bookings", tags=["Admin Bookings"])


@router.get("", dependencies=[RequirePermission("manage_bookings")])
async def admin_list_bookings(
    controller: Annotated[BookingController, Depends(get_booking_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: SortOrder = Query("desc"),
):
    return await controller.admin_list(
        limit=limit,
        offset=offset,
        sort_order=sort,
    )


@router.get(
    "/{booking_id}",
    dependencies=[RequirePermission("manage_bookings")],
)
async def admin_get_booking(
    booking_id: int,
    controller: Annotated[BookingController, Depends(get_booking_controller)],
):
    return await controller.admin_get_detail(booking_id)
