from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request

from app.api.v1.deps.controllers import get_package_controller
from app.controllers.package_controller import PackageController

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    controller: Annotated[PackageController, Depends(get_package_controller)],
    stripe_signature: str | None = Header(None, alias="stripe-signature"),
):
    payload = await request.body()
    return await controller.stripe_webhook(payload, stripe_signature)
