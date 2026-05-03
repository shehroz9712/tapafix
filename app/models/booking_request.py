from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class BookingRequest(Base, TimestampMixin):
    __tablename__ = "booking_requests"
    __table_args__ = (
        UniqueConstraint("booking_id", "provider_id", name="uq_booking_requests_booking_provider"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="requests")
    provider: Mapped["User"] = relationship("User", foreign_keys=[provider_id])
