from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission, get_current_user, require_admin
from app.api.v1.deps.controllers import (
    get_admin_controller,
    get_category_controller,
    get_package_controller,
    get_provider_profile_controller,
    get_role_controller,
    get_subcategory_controller,
)
from app.controllers.admin_controller import AdminController
from app.controllers.category_controller import CategoryController
from app.controllers.package_controller import PackageController
from app.controllers.provider_profile_controller import ProviderProfileController
from app.controllers.role_controller import RoleController
from app.controllers.subcategory_controller import SubCategoryController
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, SortOrder, SubCategoryCreate, SubCategoryUpdate
from app.schemas.package import PackageCreate, PackageUpdate
from app.schemas.provider_profile import ProviderListingVerificationUpdate
from app.schemas.rbac import RoleAssignPermissions, RoleAssignUser, RoleCreate

router = APIRouter(dependencies=[require_admin()])


@router.get("/users", dependencies=[RequirePermission("manage_users")])
async def admin_list_users(
    admin: Annotated[User, Depends(get_current_user)],
    controller: Annotated[AdminController, Depends(get_admin_controller)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await controller.list_users(admin, skip=skip, limit=limit)


@router.post("/rbac/roles", dependencies=[RequirePermission("manage_roles")])
async def create_role(
    payload: RoleCreate,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.create_role(payload)


@router.get("/rbac/roles", dependencies=[RequirePermission("manage_roles")])
async def list_roles(
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.list_roles()


@router.get("/rbac/permissions", dependencies=[RequirePermission("manage_roles")])
async def list_permissions(
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.list_permissions()


@router.post(
    "/rbac/roles/{role_id}/permissions",
    dependencies=[RequirePermission("manage_roles")],
)
async def assign_role_permissions(
    role_id: int,
    payload: RoleAssignPermissions,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.assign_permissions(role_id, payload)


@router.post("/rbac/users/{user_id}/role", dependencies=[RequirePermission("manage_roles")])
async def assign_user_role(
    user_id: int,
    payload: RoleAssignUser,
    controller: Annotated[RoleController, Depends(get_role_controller)],
):
    return await controller.assign_user_role(user_id=user_id, payload=payload)


@router.post("/categories", dependencies=[RequirePermission("manage_categories")])
async def create_category(
    payload: CategoryCreate,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
):
    return await controller.create(payload)


@router.get("/categories", dependencies=[RequirePermission("manage_categories")])
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


@router.get("/categories/{category_id}", dependencies=[RequirePermission("manage_categories")])
async def get_category(
    category_id: int,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
    include_subcategories: bool = Query(True),
):
    return await controller.get_by_id(category_id, include_subcategories=include_subcategories)


@router.put("/categories/{category_id}", dependencies=[RequirePermission("manage_categories")])
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
):
    return await controller.update(category_id, payload)


@router.delete("/categories/{category_id}", dependencies=[RequirePermission("manage_categories")])
async def delete_category(
    category_id: int,
    controller: Annotated[CategoryController, Depends(get_category_controller)],
):
    return await controller.delete(category_id)


@router.get(
    "/categories/{category_id}/subcategories",
    dependencies=[RequirePermission("manage_subcategories")],
)
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


@router.post("/subcategories", dependencies=[RequirePermission("manage_subcategories")])
async def create_subcategory(
    payload: SubCategoryCreate,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.create(payload)


@router.get("/subcategories", dependencies=[RequirePermission("manage_subcategories")])
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


@router.get("/subcategories/{subcategory_id}", dependencies=[RequirePermission("manage_subcategories")])
async def get_subcategory(
    subcategory_id: int,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.get_by_id(subcategory_id)


@router.put("/subcategories/{subcategory_id}", dependencies=[RequirePermission("manage_subcategories")])
async def update_subcategory(
    subcategory_id: int,
    payload: SubCategoryUpdate,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.update(subcategory_id, payload)


@router.delete("/subcategories/{subcategory_id}", dependencies=[RequirePermission("manage_subcategories")])
async def delete_subcategory(
    subcategory_id: int,
    controller: Annotated[SubCategoryController, Depends(get_subcategory_controller)],
):
    return await controller.delete(subcategory_id)


@router.patch(
    "/providers/{user_id}/listing-verification",
    dependencies=[RequirePermission("manage_users")],
)
async def admin_provider_listing_verification(
    user_id: int,
    payload: ProviderListingVerificationUpdate,
    controller: Annotated[
        ProviderProfileController, Depends(get_provider_profile_controller)
    ],
):
    return await controller.admin_set_listing_verified(user_id, payload)


@router.post("/packages", dependencies=[RequirePermission("manage_packages")])
async def create_package(
    payload: PackageCreate,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.create(payload)


@router.get("/packages", dependencies=[RequirePermission("manage_packages")])
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


@router.get("/packages/{package_id}", dependencies=[RequirePermission("manage_packages")])
async def get_package(
    package_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_by_id(package_id)


@router.put("/packages/{package_id}", dependencies=[RequirePermission("manage_packages")])
async def update_package(
    package_id: int,
    payload: PackageUpdate,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.update(package_id, payload)


@router.delete("/packages/{package_id}", dependencies=[RequirePermission("manage_packages")])
async def delete_package(
    package_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.delete(package_id)


@router.get("/transactions", dependencies=[RequirePermission("manage_transactions")])
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
    "/transactions/{transaction_id}",
    dependencies=[RequirePermission("manage_transactions")],
)
async def get_transaction(
    transaction_id: int,
    controller: Annotated[PackageController, Depends(get_package_controller)],
):
    return await controller.get_transaction_by_id(transaction_id)
