from fastapi import APIRouter

from app.api.v1.admin.routes import router as admin_router
from app.api.v1.provider.routes import router as provider_router
from app.api.v1.routes import auth, future
from app.api.v1.user.routes import router as user_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(provider_router, prefix="/provider", tags=["provider"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(future.router)
