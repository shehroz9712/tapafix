from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models import login_as as login_as_const

if TYPE_CHECKING:
    from app.models.password_reset_token import PasswordResetToken
    from app.models.provider_profile import ProviderProfile
    from app.models.role import Role


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(32), nullable=False, default="email", index=True
    )
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    login_as: Mapped[str] = mapped_column(
        Enum(*login_as_const.ALL, name="account_role_enum"),
        nullable=False,
        default=login_as_const.USER,
        index=True,
    )
    role_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    assigned_role: Mapped[Optional["Role"]] = relationship(
        "Role", back_populates="users"
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    provider_profile: Mapped[Optional["ProviderProfile"]] = relationship(
        "ProviderProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def role_name(self) -> str | None:
        if self.assigned_role is None:
            return None
        return self.assigned_role.name
