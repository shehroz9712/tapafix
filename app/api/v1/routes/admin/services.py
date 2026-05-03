from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import RequirePermission
from app.api.v1.deps.controllers import get_service_controller
from app.controllers.service_controller import ServiceController
from app.schemas.category import SortOrder
from app.schemas.service import ServiceCreate, ServiceUpdate

router = APIRouter(prefix="/services", tags=["Admin Services"])


@router.post("", dependencies=[RequirePermission("manage_services")])
async def admin_create_service(
    payload: ServiceCreate,
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    return await controller.admin_create(payload)


@router.get("", dependencies=[RequirePermission("manage_services")])
async def admin_list_services(
    controller: Annotated[ServiceController, Depends(get_service_controller)],
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: SortOrder = Query("desc"),
):
    return await controller.admin_get_all(
        limit=limit,
        offset=offset,
        sort_order=sort,
    )


@router.get(
    "/{service_id}",
    dependencies=[RequirePermission("manage_services")],
)
async def admin_get_service(
    service_id: int,
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    return await controller.admin_get_by_id(service_id)


@router.put(
    "/{service_id}",
    dependencies=[RequirePermission("manage_services")],
)
async def admin_update_service(
    service_id: int,
    payload: ServiceUpdate,
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    return await controller.admin_update(service_id, payload)


@router.delete(
    "/{service_id}",
    dependencies=[RequirePermission("manage_services")],
)
async def admin_delete_service(
    service_id: int,
    controller: Annotated[ServiceController, Depends(get_service_controller)],
):
    return await controller.admin_delete(service_id)
