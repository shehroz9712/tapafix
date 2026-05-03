from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission
from app.api.v1.deps.controllers import get_package_controller
from app.controllers.package_controller import PackageController
from app.schemas.category import SortOrder
from app.schemas.package import PackageCreate, PackageUpdate

router = APIRouter(prefix="/packages", tags=["Admin Packages"])


@router.post("", dependencies=[RequirePermission("manage_packages")])
async def create_package(
    payload: PackageCreate,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.create(payload)


@router.get("", dependencies=[RequirePermission("manage_packages")])
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


@router.get(
    "/{package_id}",
    dependencies=[RequirePermission("manage_packages")],
)
async def get_package(
    package_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_by_id(package_id)


@router.put(
    "/{package_id}",
    dependencies=[RequirePermission("manage_packages")],
)
async def update_package(
    package_id: int,
    payload: PackageUpdate,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.update(package_id, payload)


@router.delete(
    "/{package_id}",
    dependencies=[RequirePermission("manage_packages")],
)
async def delete_package(
    package_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.delete(package_id)
