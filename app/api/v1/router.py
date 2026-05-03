from fastapi import APIRouter

from app.api.v1.routes import auth, chat, payments, providers_public
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.provider import router as provider_router
from app.api.v1.routes.user import router as user_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat")
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(provider_router, prefix="/provider", tags=["provider"])
api_router.include_router(providers_public.router, prefix="/providers", tags=["providers"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(payments.router)
