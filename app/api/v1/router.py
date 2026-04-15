from fastapi import APIRouter

from app.api.v1.routes import (
    admin,
    auth,
    categories,
    future,
    role_routes,
    subcategories,
    users,
    vendor,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(role_routes.router, prefix="/admin", tags=["admin-rbac"])
api_router.include_router(vendor.router, prefix="/vendor", tags=["vendor"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(subcategories.router, tags=["subcategories"])
api_router.include_router(future.router)
