from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import get_current_user, require_role
from app.api.v1.deps.controllers import (
    get_category_controller,
    get_package_controller,
    get_subcategory_controller,
    get_user_controller,
)
from app.controllers.category_controller import CategoryController
from app.controllers.package_controller import PackageController
from app.controllers.subcategory_controller import SubCategoryController
from app.controllers.user_controller import UserController
from app.models.user import User
from app.schemas.category import SortOrder

router = APIRouter(dependencies=[require_role(["user", "provider"])])


@router.get("/me")
async def read_me(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[UserController, Depends(get_user_controller)],
):
    return await controller.me(current_user)


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


@router.get("/packages")
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


@router.get("/packages/{package_id}")
async def get_package(
    package_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_by_id(package_id)


@router.post("/packages/{package_id}/buy")
async def buy_package(
    package_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.create_checkout(
        current_user=current_user,
        package_id=package_id,
    )


@router.get("/transactions")
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


@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_user_transaction_by_id(transaction_id, current_user)
