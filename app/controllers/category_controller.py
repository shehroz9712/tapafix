from __future__ import annotations

from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService


class CategoryController(BaseController):
    def __init__(self, service: CategoryService):
        self._service = service

    async def create(self, payload: CategoryCreate) -> JSONResponse:
        category = await self._service.create(payload)
        return self.respond_success(self._service.serialize(category), "Category created", 201)

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
        include_subcategories: bool,
    ) -> JSONResponse:
        rows = await self._service.get_all(
            limit=limit,
            offset=offset,
            is_active=is_active,
            sort_order=sort_order,
            include_subcategories=include_subcategories,
        )
        data = [
            self._service.serialize(row, include_subcategories=include_subcategories)
            for row in rows
        ]
        return self.respond_success(data, "Categories retrieved")

    async def get_by_id(self, category_id: int, *, include_subcategories: bool) -> JSONResponse:
        category = await self._service.get_by_id(
            category_id,
            include_subcategories=include_subcategories,
        )
        return self.respond_success(
            self._service.serialize(category, include_subcategories=include_subcategories),
            "Category retrieved",
        )

    async def update(self, category_id: int, payload: CategoryUpdate) -> JSONResponse:
        category = await self._service.update(category_id, payload)
        return self.respond_success(self._service.serialize(category), "Category updated")

    async def delete(self, category_id: int) -> JSONResponse:
        await self._service.delete(category_id)
        return self.respond_success(None, "Category deleted")
