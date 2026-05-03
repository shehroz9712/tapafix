from fastapi import APIRouter

from app.api.v1.deps.auth import require_provider

from . import bookings, dashboard, profile, services

router = APIRouter(dependencies=[require_provider()])
router.include_router(dashboard.router)
router.include_router(bookings.router)
router.include_router(profile.router)
router.include_router(services.router)
