from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission
from app.api.v1.deps.controllers import get_package_controller
from app.controllers.package_controller import PackageController
from app.schemas.category import SortOrder

router = APIRouter(prefix="/transactions", tags=["Admin Transactions"])


@router.get("", dependencies=[RequirePermission("manage_transactions")])
async def list_transactions(
    controller: Annotated[PackageController, Depends(get_package_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: int | None = Query(None, ge=1),
    status: str | None = Query(None),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_all_transactions(
        limit=limit,
        offset=offset,
        user_id=user_id,
        status=status,
        sort_order=sort,
    )


@router.get(
    "/{transaction_id}",
    dependencies=[RequirePermission("manage_transactions")],
)
async def get_transaction(
    transaction_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_transaction_by_id(transaction_id)
