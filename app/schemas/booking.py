from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.availability import _parse_hhmm

BookingCancellationReasonType = Literal[
    "customer_plans_changed",
    "found_another_provider",
    "schedule_no_longer_works",
    "price_or_budget",
    "duplicate_or_mistake",
    "service_no_longer_needed",
    "provider_issue",
    "other",
]


class BookingCancel(BaseModel):
    reason_type: BookingCancellationReasonType = Field(
        ...,
        description="Structured reason for cancellation.",
    )
    cancellation_note: str | None = Field(
        None,
        max_length=2000,
        description="Optional extra detail; required when reason_type is other.",
    )

    @model_validator(mode="after")
    def other_requires_note(self) -> BookingCancel:
        if self.reason_type == "other":
            text = (self.cancellation_note or "").strip()
            if not text:
                raise ValueError("cancellation_note is required when reason_type is other")
        return self


class BookingCreate(BaseModel):
    category_id: int = Field(..., ge=1)
    subcategory_id: int = Field(..., ge=1)
    service_id: int = Field(..., ge=1)
    scheduled_date: date
    start_time: str = Field(..., min_length=5, max_length=5, description="Start of time window, 24h HH:MM")
    end_time: str = Field(..., min_length=5, max_length=5, description="End of time window, 24h HH:MM")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    note: str | None = Field(None, max_length=2000)
    is_broadcast: bool = False

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_hhmm(cls, v: str) -> str:
        if _parse_hhmm(v) is None:
            raise ValueError("time must be HH:MM (24-hour)")
        return v.strip()

    @model_validator(mode="after")
    def end_after_start(self) -> BookingCreate:
        a, b = _parse_hhmm(self.start_time), _parse_hhmm(self.end_time)
        if a is not None and b is not None and a >= b:
            raise ValueError("end_time must be after start_time on the same day")
        return self


class BookingCountsMixin(BaseModel):
    total_requests: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    pending_count: int = 0
    auto_closed_count: int = 0


class BookingResponse(BaseModel, BookingCountsMixin):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category_id: int
    subcategory_id: int
    service_id: int
    scheduled_date: date | None = None
    start_time: str | None = None
    end_time: str | None = None
    latitude: float
    longitude: float
    note: str | None = None
    is_broadcast: bool
    status: str
    cancellation_reason_type: str | None = None
    cancellation_note: str | None = None
    cancelled_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BookingRequestCreate(BaseModel):
    message: str | None = Field(None, max_length=2000)


class BookingRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    provider_id: int
    status: str
    message: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BookingDetailResponse(BaseModel, BookingCountsMixin):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category_id: int
    subcategory_id: int
    service_id: int
    scheduled_date: date | None = None
    start_time: str | None = None
    end_time: str | None = None
    latitude: float
    longitude: float
    note: str | None = None
    is_broadcast: bool
    status: str
    cancellation_reason_type: str | None = None
    cancellation_note: str | None = None
    cancelled_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    requests: list[BookingRequestResponse] = Field(default_factory=list)
