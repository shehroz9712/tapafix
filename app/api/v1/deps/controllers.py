"""Controller factories for FastAPI Depends (one session per request via services)."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.db import get_db
from app.controllers.admin_controller import AdminController
from app.controllers.auth_controller import AuthController
from app.controllers.category_controller import CategoryController
from app.controllers.future_modules_controller import FutureModulesController
from app.controllers.package_controller import PackageController
from app.controllers.role_controller import RoleController
from app.controllers.subcategory_controller import SubCategoryController
from app.controllers.provider_profile_controller import ProviderProfileController
from app.controllers.user_controller import UserController
from app.controllers.vendor_controller import VendorController
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.future_modules_service import FutureModulesService
from app.services.package_service import PackageService
from app.services.provider_profile_service import ProviderProfileService
from app.services.role_service import RoleService
from app.services.subcategory_service import SubCategoryService
from app.services.user_service import UserService
from app.services.vendor_service import VendorService


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    return AuthService(session)


def get_auth_controller(
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthController:
    return AuthController(service)


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    return UserService(session)


def get_user_controller(
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserController:
    return UserController(service)


def get_admin_controller(
    service: Annotated[UserService, Depends(get_user_service)],
) -> AdminController:
    return AdminController(service)


def get_role_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RoleService:
    return RoleService(session)


def get_role_controller(
    service: Annotated[RoleService, Depends(get_role_service)],
) -> RoleController:
    return RoleController(service)


def get_category_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryService:
    return CategoryService(session)


def get_category_controller(
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryController:
    return CategoryController(service)


def get_subcategory_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SubCategoryService:
    return SubCategoryService(session)


def get_subcategory_controller(
    service: Annotated[SubCategoryService, Depends(get_subcategory_service)],
) -> SubCategoryController:
    return SubCategoryController(service)


def get_vendor_service() -> VendorService:
    return VendorService()


def get_vendor_controller(
    service: Annotated[VendorService, Depends(get_vendor_service)],
) -> VendorController:
    return VendorController(service)


def get_provider_profile_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ProviderProfileService:
    return ProviderProfileService(session)


def get_provider_profile_controller(
    service: Annotated[ProviderProfileService, Depends(get_provider_profile_service)],
) -> ProviderProfileController:
    return ProviderProfileController(service)


def get_package_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> PackageService:
    return PackageService(session)


def get_package_controller(
    service: Annotated[PackageService, Depends(get_package_service)],
) -> PackageController:
    return PackageController(service)


def get_future_modules_service() -> FutureModulesService:
    return FutureModulesService()


def get_future_modules_controller(
    service: Annotated[FutureModulesService, Depends(get_future_modules_service)],
) -> FutureModulesController:
    return FutureModulesController(service)
