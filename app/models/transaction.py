from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.package_purchase import PackagePurchase
    from app.models.user import User


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    package_purchase_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("package_purchases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="usd")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="stripe")
    provider_session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    package_purchase: Mapped["PackagePurchase"] = relationship(
        "PackagePurchase",
        back_populates="transactions",
    )
