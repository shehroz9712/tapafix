from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.controllers import (
    get_category_controller,
    get_subcategory_controller,
)
from app.controllers.category_controller import CategoryController
from app.controllers.subcategory_controller import SubCategoryController
from app.schemas.category import SortOrder

router = APIRouter(prefix="", tags=["User Catalog"])


@router.get("/categories")
async def list_categories(
    controller: Annotated[CategoryController, Depends(get_category_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_all(
        limit=limit,
        offset=offset,
        is_active=True,
        sort_order=sort,
        include_subcategories=False,
    )


@router.get("/categories/{category_id}")
async def get_category(
    category_id: int,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
):
    return await controller.get_by_id(category_id, include_subcategories=False)


@router.get("/subcategories")
async def list_subcategories(
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_all(
        limit=limit,
        offset=offset,
        sort_order=sort,
    )


@router.get("/subcategories/{subcategory_id}")
async def get_subcategory(
    subcategory_id: int,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.get_by_id(subcategory_id)


@router.get("/categories/{category_id}/subcategories")
async def get_subcategories_by_category(
    category_id: int,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: SortOrder = Query("desc"),
):
    return await controller.get_by_category(
        category_id,
        limit=limit,
        offset=offset,
        is_active=True,
        sort_order=sort,
    )
