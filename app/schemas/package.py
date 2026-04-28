from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PackageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sort: int = 0
    image: str | None = Field(None, max_length=255)
    price: float = Field(0, ge=0)
    duration: int = Field(..., ge=1)
    description: str | None = Field(None, max_length=1000)
    payment_interval: str | None = Field(None, max_length=50)
    currency: str = Field("usd", max_length=10)
    services: int | None = Field(None, ge=0)


class PackageUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    sort: int | None = None
    image: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)
    duration: int | None = Field(None, ge=1)
    description: str | None = Field(None, max_length=1000)
    payment_interval: str | None = Field(None, max_length=50)
    currency: str | None = Field(None, max_length=10)
    services: int | None = Field(None, ge=0)


class PackageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort: int
    image: str | None
    price: float
    duration: int
    description: str | None
    payment_interval: str | None
    currency: str
    services: int | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PackagePurchaseCreate(BaseModel):
    package_id: int
    payment_interval: str | None = None


class PackagePurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    package_id: int
    payment_interval: str | None
    amount: float
    currency: str
    status: str
    stripe_checkout_session_id: str | None
    stripe_payment_intent_id: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
