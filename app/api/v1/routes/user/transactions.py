from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import get_current_user
from app.api.v1.deps.controllers import get_package_controller
from app.controllers.package_controller import PackageController
from app.models.user import User
from app.schemas.category import SortOrder

router = APIRouter(prefix="/transactions", tags=["User Transactions"])


@router.get("")
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[PackageController, Depends(get_package_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_all_transactions(
        limit=limit,
        offset=offset,
        user_id=current_user.id,
        status=status,
        sort_order=sort,
    )


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_user_transaction_by_id(transaction_id, current_user)
