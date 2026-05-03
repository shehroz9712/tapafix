from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.deps.auth import require_admin

from . import bookings, categories, packages, providers, rbac, services, subcategories, transactions, users

router = APIRouter(dependencies=[require_admin()])
router.include_router(users.router)
router.include_router(bookings.router)
router.include_router(rbac.router)
router.include_router(categories.router)
router.include_router(subcategories.router)
router.include_router(providers.router)
router.include_router(packages.router)
router.include_router(services.router)
router.include_router(transactions.router)
