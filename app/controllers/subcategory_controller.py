from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.schemas.category import SubCategoryCreate, SubCategoryUpdate
from app.services.subcategory_service import SubCategoryService


class SubCategoryController(BaseController):
    def __init__(self, service: SubCategoryService):
        self._service = service

    async def create(self, payload: SubCategoryCreate) -> JSONResponse:
        row = await self._service.create(payload)
        return self.respond_success(self._service.serialize(row), "Subcategory created", 201)

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
    ) -> JSONResponse:
        rows = await self._service.get_all(
            limit=limit,
            offset=offset,
            is_active=is_active,
            sort_order=sort_order,
        )
        data = [self._service.serialize(row) for row in rows]
        return self.respond_success(data, "Subcategories retrieved")

    async def get_by_id(self, subcategory_id: int) -> JSONResponse:
        row = await self._service.get_by_id(subcategory_id)
        return self.respond_success(self._service.serialize(row), "Subcategory retrieved")

    async def get_by_category(
        self,
        category_id: int,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
    ) -> JSONResponse:
        rows = await self._service.get_by_category_id(
            category_id,
            limit=limit,
            offset=offset,
            is_active=is_active,
            sort_order=sort_order,
        )
        data = [self._service.serialize(row) for row in rows]
        return self.respond_success(data, "Subcategories retrieved")

    async def update(self, subcategory_id: int, payload: SubCategoryUpdate) -> JSONResponse:
        row = await self._service.update(subcategory_id, payload)
        return self.respond_success(self._service.serialize(row), "Subcategory updated")

    async def delete(self, subcategory_id: int) -> JSONResponse:
        await self._service.delete(subcategory_id)
        return self.respond_success(None, "Subcategory deleted")
