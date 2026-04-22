from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subcategory import SubCategory
from app.repositories.base import BaseRepository


class SubCategoryRepository(BaseRepository[SubCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SubCategory)

    async def create(
        self,
        *,
        category_id: int,
        name: str,
        description: str | None,
        is_active: bool,
    ) -> SubCategory:
        return await super().create(
            obj_in={
                "category_id": category_id,
                "name": name.strip(),
                "description": description,
                "is_active": is_active,
            }
        )

    async def get_by_id(self, subcategory_id: int) -> SubCategory | None:
        stmt = select(SubCategory).where(SubCategory.id == subcategory_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_by_ids(self, ids: list[int]) -> list[SubCategory]:
        if not ids:
            return []
        stmt = select(SubCategory).where(
            SubCategory.id.in_(ids),
            SubCategory.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_category_id(
        self,
        category_id: int,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
    ) -> list[SubCategory]:
        stmt = select(SubCategory).where(SubCategory.category_id == category_id)
        if is_active is not None:
            stmt = stmt.where(SubCategory.is_active == is_active)
        if sort_order == "asc":
            stmt = stmt.order_by(SubCategory.created_at.asc())
        else:
            stmt = stmt.order_by(SubCategory.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
    ) -> list[SubCategory]:
        stmt = select(SubCategory)
        if is_active is not None:
            stmt = stmt.where(SubCategory.is_active == is_active)
        if sort_order == "asc":
            stmt = stmt.order_by(SubCategory.created_at.asc())
        else:
            stmt = stmt.order_by(SubCategory.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_category_and_name(self, category_id: int, name: str) -> SubCategory | None:
        stmt = select(SubCategory).where(
            SubCategory.category_id == category_id,
            func.lower(SubCategory.name) == name.strip().lower(),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, subcategory: SubCategory, *, data: dict) -> SubCategory:
        for key, value in data.items():
            setattr(subcategory, key, value)
        await self.session.flush()
        await self.session.refresh(subcategory)
        return subcategory

    async def delete(self, subcategory: SubCategory) -> None:
        await self.session.delete(subcategory)
        await self.session.flush()
