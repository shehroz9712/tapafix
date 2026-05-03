from __future__ import annotations

from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.schemas.category import SortOrder
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.service_service import ServiceService


class ServiceController(BaseController):
    def __init__(self, service: ServiceService):
        self._service = service

    async def admin_create(self, payload: ServiceCreate) -> JSONResponse:
        row = await self._service.admin_create(payload)
        return self.respond_success(self._service.serialize(row), "Service created", 201)

    async def admin_get_all(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: SortOrder,
    ) -> JSONResponse:
        rows = await self._service.admin_get_all(
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )
        data = [self._service.serialize(r) for r in rows]
        return self.respond_success(data, "Services retrieved")

    async def admin_get_by_id(self, service_id: int) -> JSONResponse:
        row = await self._service.admin_get_by_id(service_id)
        return self.respond_success(self._service.serialize(row), "Service retrieved")

    async def admin_update(self, service_id: int, payload: ServiceUpdate) -> JSONResponse:
        row = await self._service.admin_update(service_id, payload)
        return self.respond_success(self._service.serialize(row), "Service updated")

    async def admin_delete(self, service_id: int) -> JSONResponse:
        await self._service.admin_delete(service_id)
        return self.respond_success(None, "Service deleted")

    async def user_create(self, current_user: User, payload: ServiceCreate) -> JSONResponse:
        row = await self._service.user_create_request(current_user, payload)
        return self.respond_success(self._service.serialize(row), "Service request created", 201)

    async def user_list(self, current_user: User) -> JSONResponse:
        rows = await self._service.user_list_visible(current_user)
        data = [self._service.serialize(r) for r in rows]
        return self.respond_success(data, "Services retrieved")

    async def user_get(self, current_user: User, service_id: int) -> JSONResponse:
        row = await self._service.user_get_visible(current_user, service_id)
        return self.respond_success(self._service.serialize(row), "Service retrieved")

    async def provider_create(self, current_user: User, payload: ServiceCreate) -> JSONResponse:
        row = await self._service.provider_create_listing(current_user, payload)
        return self.respond_success(self._service.serialize(row), "Service created", 201)

    async def provider_list(self, current_user: User) -> JSONResponse:
        rows = await self._service.provider_list_mine(current_user)
        data = [self._service.serialize(r) for r in rows]
        return self.respond_success(data, "Services retrieved")
