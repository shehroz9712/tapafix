from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, EmailStr, Field, model_validator

SelfServeLoginAs = Literal["user", "provider"]


class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    country: str = Field(..., min_length=1, max_length=120)
    phone: str | None = Field(None, max_length=32)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    login_as: SelfServeLoginAs = Field(
        "user",
        description="Customer (user) or handyman (provider). Admins are assigned separately.",
    )

    @model_validator(mode="after")
    def latitude_longitude_pair(self) -> UserCreate:
        if (self.latitude is None) ^ (self.longitude is None):
            raise ValueError("latitude and longitude must both be set or both omitted")
        return self


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    country: str | None = Field(None, min_length=1, max_length=120)
    phone: str | None = Field(None, max_length=32)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    def latitude_longitude_pair(self) -> UserProfileUpdate:
        if (self.latitude is None) ^ (self.longitude is None):
            raise ValueError("latitude and longitude must both be set or both omitted")
        return self


class UserPublic(BaseModel):
    id: int
    first_name: str
    last_name: str
    name: str
    email: str
    phone: str | None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
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
