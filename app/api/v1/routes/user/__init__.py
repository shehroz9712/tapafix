from fastapi import APIRouter

from app.api.v1.deps.auth import require_role

from . import bookings, catalog, packages, profile, services, transactions, workers

router = APIRouter(dependencies=[require_role(["user", "provider"])])
router.include_router(profile.router)
router.include_router(workers.router)
router.include_router(bookings.router)
router.include_router(catalog.router)
router.include_router(packages.router)
router.include_router(services.router)
router.include_router(transactions.router)
