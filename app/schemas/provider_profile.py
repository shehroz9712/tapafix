from __future__ import annotations

import re
from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from app.utils.availability import _normalize_day, _parse_hhmm

DEMO_PROVIDER_OTP = "123654"

_WEEKDAYS = frozenset(
    ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
)
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class AvailabilitySlot(BaseModel):
    day: str = Field(..., min_length=1, max_length=16)
    start_time: str = Field(..., min_length=5, max_length=5)
    end_time: str = Field(..., min_length=5, max_length=5)

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: str) -> str:
        norm = _normalize_day(v)
        if norm is None or norm not in _WEEKDAYS:
            raise ValueError("day must be a full English weekday (e.g. Monday)")
        return norm

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not _TIME_RE.match(v.strip()):
            raise ValueError("time must be HH:MM in 24-hour format")
        if _parse_hhmm(v.strip()) is None:
            raise ValueError("invalid time")
        return v.strip()


class ProviderProfileBase(BaseModel):
    """Provider-only listing fields. Name, email, and phone come from ``users``."""

    category_ids: list[Annotated[int, Field(ge=1)]] = Field(default_factory=list)
    subcategory_ids: list[Annotated[int, Field(ge=1)]] = Field(default_factory=list)
    years_of_experience: int = Field(..., ge=0, le=80)
    price_per_job: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    price_per_hour: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    city: str = Field(..., min_length=1, max_length=120)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    service_radius_km: float = Field(..., gt=0, le=5000)
    cnic_front: HttpUrl | None = None
    cnic_back: HttpUrl | None = None
    certificates: list[HttpUrl] = Field(default_factory=list)
    available_days: list[AvailabilitySlot] = Field(default_factory=list)

    @field_validator("category_ids")
    @classmethod
    def unique_category_ids(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("category_ids must be unique")
        return v

    @field_validator("subcategory_ids")
    @classmethod
    def unique_subcategory_ids(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("subcategory_ids must be unique")
        return v

    @model_validator(mode="after")
    def listing_non_empty(self) -> ProviderProfileBase:
        if not self.available_days:
            raise ValueError("available_days must contain at least one slot")
        if not self.category_ids:
            raise ValueError("category_ids must not be empty")
        if not self.subcategory_ids:
            raise ValueError("subcategory_ids must not be empty")
        return self


class ProviderProfileCreate(ProviderProfileBase):
    """Full payload for POST /provider/profile (complete or replace listing data)."""

    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

    @field_validator("otp", mode="before")
    @classmethod
    def strip_otp(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("otp")
    @classmethod
    def validate_demo_otp(cls, v: str) -> str:
        if v != DEMO_PROVIDER_OTP:
            raise ValueError("Incorrect verification code")
        return v


class ProviderProfilePatch(BaseModel):
    """Partial update for PATCH /provider/profile (identity is not editable here)."""

    category_ids: list[Annotated[int, Field(ge=1)]] | None = None
    subcategory_ids: list[Annotated[int, Field(ge=1)]] | None = None
    years_of_experience: int | None = Field(None, ge=0, le=80)
    price_per_job: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    price_per_hour: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    city: str | None = Field(None, min_length=1, max_length=120)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    service_radius_km: float | None = Field(None, gt=0, le=5000)
    cnic_front: HttpUrl | None = None
    cnic_back: HttpUrl | None = None
    certificates: list[HttpUrl] | None = None
    available_days: list[AvailabilitySlot] | None = None

    @field_validator("category_ids")
    @classmethod
    def unique_category_ids(cls, v: list[int] | None) -> list[int] | None:
        if v is None:
            return None
        if len(v) != len(set(v)):
            raise ValueError("category_ids must be unique")
        return v

    @field_validator("subcategory_ids")
    @classmethod
    def unique_subcategory_ids(cls, v: list[int] | None) -> list[int] | None:
        if v is None:
            return None
        if len(v) != len(set(v)):
            raise ValueError("subcategory_ids must be unique")
        return v

    @model_validator(mode="after")
    def patch_no_empty_taxonomy(self) -> ProviderProfilePatch:
        if self.category_ids is not None and not self.category_ids:
            raise ValueError("category_ids must not be empty")
        if self.subcategory_ids is not None and not self.subcategory_ids:
            raise ValueError("subcategory_ids must not be empty")
        return self


class ProviderListingVerificationUpdate(BaseModel):
    """Admin: mark provider listing as verified after review (e.g. CNIC)."""

    is_listing_verified: bool


class ProviderProfileOut(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: str | None
    is_listing_verified: bool
    otp_verified: bool = False
    category_ids: list[int]
    subcategory_ids: list[int]
    years_of_experience: int | None
    price_per_job: float | None
    price_per_hour: float | None
    city: str | None
    latitude: float | None
    longitude: float | None
    service_radius_km: float | None
    cnic_front: str | None = None
    cnic_back: str | None = None
    certificates: list[str]
    available_days: list[dict[str, Any]]

    model_config = {"from_attributes": True}

    @classmethod
    def from_profile_and_user(
        cls,
        profile: Any,
        user: Any,
        *,
        otp_verified: bool = False,
    ) -> ProviderProfileOut:
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            is_listing_verified=bool(profile.is_listing_verified),
            otp_verified=otp_verified,
            category_ids=profile.category_ids or [],
            subcategory_ids=profile.subcategory_ids or [],
            years_of_experience=profile.years_of_experience,
            price_per_job=profile.price_per_job,
            price_per_hour=profile.price_per_hour,
            city=profile.city,
            latitude=profile.latitude,
            longitude=profile.longitude,
            service_radius_km=profile.service_radius_km,
            cnic_front=profile.cnic_front,
            cnic_back=profile.cnic_back,
            certificates=profile.certificates or [],
            available_days=profile.available_days or [],
        )

    @field_validator("category_ids", "subcategory_ids", mode="before")
    @classmethod
    def coerce_id_lists(cls, v: Any) -> list[int]:
        if not v:
            return []
        return [int(x) for x in v]

    @field_validator("certificates", mode="before")
    @classmethod
    def coerce_cert_list(cls, v: Any) -> list[str]:
        if not v:
            return []
        return [str(x) for x in v]

    @field_validator("price_per_job", "price_per_hour", "latitude", "longitude", "service_radius_km", mode="before")
    @classmethod
    def coerce_numeric(cls, v: Any) -> Any:
        if v is None:
            return None
        return float(v)


class ProviderSearchItem(ProviderProfileOut):
    distance_km: float


class ProviderSearchQuery(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category_id: int | None = Field(None, ge=1)
    subcategory_id: int | None = Field(None, ge=1)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
