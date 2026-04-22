from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def create(self, *, name: str, description: str | None, is_active: bool) -> Category:
        return await super().create(
            obj_in={
                "name": name.strip(),
                "description": description,
                "is_active": is_active,
            }
        )

    async def get_by_id(self, category_id: int, *, include_subcategories: bool = False) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        if include_subcategories:
            stmt = stmt.options(selectinload(Category.subcategories))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(func.lower(Category.name) == name.strip().lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_active_by_ids(self, ids: list[int]) -> int:
        if not ids:
            return 0
        stmt = select(func.count()).select_from(Category).where(
            Category.id.in_(ids),
            Category.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
        include_subcategories: bool = False,
    ) -> list[Category]:
        stmt = select(Category)
        if include_subcategories:
            stmt = stmt.options(selectinload(Category.subcategories))
        if is_active is not None:
            stmt = stmt.where(Category.is_active == is_active)
        if sort_order == "asc":
            stmt = stmt.order_by(Category.created_at.asc())
        else:
            stmt = stmt.order_by(Category.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, category: Category, *, data: dict) -> Category:
        for key, value in data.items():
            setattr(category, key, value)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
        await self.session.flush()
