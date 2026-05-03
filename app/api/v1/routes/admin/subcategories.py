from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission
from app.api.v1.deps.controllers import get_subcategory_controller
from app.controllers.subcategory_controller import SubCategoryController
from app.schemas.category import SortOrder, SubCategoryCreate, SubCategoryUpdate

router = APIRouter(prefix="/subcategories", tags=["Admin Subcategories"])


@router.post("", dependencies=[RequirePermission("manage_subcategories")])
async def create_subcategory(
    payload: SubCategoryCreate,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.create(payload)


@router.get("", dependencies=[RequirePermission("manage_subcategories")])
async def list_subcategories(
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: bool | None = Query(None),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_all(
        limit=limit,
        offset=offset,
        is_active=is_active,
        sort_order=sort,
    )


@router.get(
    "/{subcategory_id}",
    dependencies=[RequirePermission("manage_subcategories")],
)
async def get_subcategory(
    subcategory_id: int,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.get_by_id(subcategory_id)


@router.put(
    "/{subcategory_id}",
    dependencies=[RequirePermission("manage_subcategories")],
)
async def update_subcategory(
    subcategory_id: int,
    payload: SubCategoryUpdate,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.update(subcategory_id, payload)


@router.delete(
    "/{subcategory_id}",
    dependencies=[RequirePermission("manage_subcategories")],
)
async def delete_subcategory(
    subcategory_id: int,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.delete(subcategory_id)
