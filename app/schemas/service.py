from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ServiceKind = Literal["user_request", "provider_listing"]


class ServiceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    user_id: int | None = Field(None, ge=1)
    service_kind: ServiceKind | None = None


class ServiceUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    service_kind: ServiceKind | None = None
    user_id: int | None = Field(None, ge=1)


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    service_kind: str
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
