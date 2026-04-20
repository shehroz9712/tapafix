from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, EmailStr, Field

SelfServeLoginAs = Literal["user", "provider"]


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(None, max_length=32)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    login_as: SelfServeLoginAs = Field(
        "user",
        description="Customer (user) or handyman (provider). Admins are assigned separately.",
    )


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    provider: str = "email"
    avatar_url: str | None = None
    login_as: str
    role: str | None = Field(None, validation_alias=AliasChoices("role_name"))
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserAdminOut(UserPublic):
    role_id: int | None = None
    created_at: datetime | None = None
