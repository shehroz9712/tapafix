from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.booking_request import BookingRequest
    from app.models.user import User


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    subcategory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subcategories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("services.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)

    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    end_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_broadcast: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open", index=True)

    cancellation_reason_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    cancellation_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pending_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    auto_closed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    customer: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    requests: Mapped[list["BookingRequest"]] = relationship(
        "BookingRequest",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
