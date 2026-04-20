from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission, require_admin
from app.api.v1.deps.controllers import (
    get_category_controller,
    get_subcategory_controller,
)
from app.controllers.category_controller import CategoryController
from app.controllers.subcategory_controller import SubCategoryController
from app.schemas.category import CategoryCreate, CategoryUpdate, SortOrder

router = APIRouter(
    dependencies=[require_admin(), RequirePermission("manage_categories")],
)


@router.post("/categories")
async def create_category(
    payload: CategoryCreate,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
):
    return await controller.create(payload)


@router.get("/categories")
async def list_categories(
    controller: Annotated[CategoryController, Depends(get_category_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: bool | None = Query(None),
    sort: SortOrder = Query("desc"),
    include_subcategories: bool = Query(True),
):
    return await controller.get_all(
        limit=limit,
        offset=offset,
        is_active=is_active,
        sort_order=sort,
        include_subcategories=include_subcategories,
    )


@router.get("/categories/{category_id}")
async def get_category(
    category_id: int,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
    include_subcategories: bool = Query(True),
):
    return await controller.get_by_id(category_id, include_subcategories=include_subcategories)


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
):
    return await controller.update(category_id, payload)


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
):
    return await controller.delete(category_id)


@router.get("/categories/{category_id}/subcategories")
async def get_subcategories_by_category(
    category_id: int,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    is_active: bool | None = Query(None),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_by_category(
        category_id,
        limit=limit,
        offset=offset,
        is_active=is_active,
        sort_order=sort,
    )
