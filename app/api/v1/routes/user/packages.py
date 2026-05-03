from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import get_current_user
from app.api.v1.deps.controllers import get_package_controller
from app.controllers.package_controller import PackageController
from app.models.user import User
from app.schemas.category import SortOrder

router = APIRouter(prefix="/packages", tags=["User Packages"])


@router.get("")
async def list_packages(
    controller: Annotated[PackageController, Depends(get_package_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_all(
        limit=limit,
        offset=offset,
        sort_order=sort,
    )


@router.get("/{package_id}")
async def get_package(
    package_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_by_id(package_id)


@router.post("/{package_id}/buy")
async def buy_package(
    package_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.create_checkout(
        current_user=current_user,
        package_id=package_id,
    )
