from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import DECIMAL, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.package_purchase import PackagePurchase


class Package(Base, TimestampMixin):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False, default=0)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_interval: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="usd")
    services: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    purchases: Mapped[list["PackagePurchase"]] = relationship(
        "PackagePurchase",
        back_populates="package",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
