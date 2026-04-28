from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    package_purchase_id: int
    amount: float
    currency: str
    status: str
    provider: str
    provider_session_id: str | None
    provider_payment_id: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
