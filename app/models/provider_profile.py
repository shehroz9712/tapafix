from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy import JSON as SAJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ProviderProfile(Base, TimestampMixin):
    """Extended listing for handyman accounts (login_as=provider).

    Public visibility (search and public GET) requires admin
    ``is_listing_verified``, location, categories, service radius, non-empty
    weekly availability, and current time within that schedule. Name, email,
    and phone are mirrored from ``users`` on each listing save for convenience;
    API responses read identity from ``users``.
    """

    __tablename__ = "provider_profiles"
    __table_args__ = (
        Index("ix_provider_profiles_lat_lng", "latitude", "longitude"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    category_ids: Mapped[list[Any]] = mapped_column(SAJSON, nullable=False)
    subcategory_ids: Mapped[list[Any]] = mapped_column(SAJSON, nullable=False)

    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_per_job: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    price_per_hour: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)

    city: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7), nullable=True)
    service_radius_km: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)

    cnic_front: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cnic_back: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    certificates: Mapped[list[Any]] = mapped_column(SAJSON, nullable=False)

    available_days: Mapped[list[Any]] = mapped_column(SAJSON, nullable=False)

    is_listing_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="provider_profile")
