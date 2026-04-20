from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.categories = CategoryRepository(session)

    async def create(self, payload: CategoryCreate) -> Category:
        existing = await self.categories.get_by_name(payload.name)
        if existing:
            raise ConflictError("Category name already exists")
        try:
            category = await self.categories.create(
                name=payload.name,
                description=payload.description,
                is_active=payload.is_active,
            )
            await self.session.commit()
            return category
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Category name already exists")

    async def get_by_id(self, category_id: int, *, include_subcategories: bool = True) -> Category:
        category = await self.categories.get_by_id(
            category_id,
            include_subcategories=include_subcategories,
        )
        if not category:
            raise NotFoundError("Category not found")
        return category

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
        include_subcategories: bool,
    ) -> list[Category]:
        return await self.categories.get_all(
            limit=limit,
            offset=offset,
            is_active=is_active,
            sort_order=sort_order,
            include_subcategories=include_subcategories,
        )

    async def update(self, category_id: int, payload: CategoryUpdate) -> Category:
        category = await self.get_by_id(category_id, include_subcategories=False)
        data = payload.model_dump(exclude_unset=True)
        if "name" in data:
            existing = await self.categories.get_by_name(data["name"])
            if existing and existing.id != category_id:
                raise ConflictError("Category name already exists")
        try:
            updated = await self.categories.update(category, data=data)
            await self.session.commit()
            return updated
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Category name already exists")

    async def delete(self, category_id: int) -> None:
        category = await self.get_by_id(category_id, include_subcategories=False)
        await self.categories.delete(category)
        await self.session.commit()

    @staticmethod
    def serialize(category: Category, include_subcategories: bool = True) -> dict:
        if not include_subcategories:
            return CategoryResponse.model_validate(
                {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "is_active": category.is_active,
                    "created_at": category.created_at,
                    "updated_at": category.updated_at,
                    "subcategories": None,
                }
            ).model_dump()
        return CategoryResponse.model_validate(category).model_dump()
