from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.subcategory import SubCategory
from app.repositories.category_repository import CategoryRepository
from app.repositories.subcategory_repository import SubCategoryRepository
from app.schemas.category import SubCategoryCreate, SubCategoryResponse, SubCategoryUpdate


class SubCategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.categories = CategoryRepository(session)
        self.subcategories = SubCategoryRepository(session)

    async def create(self, payload: SubCategoryCreate) -> SubCategory:
        category = await self.categories.get_by_id(payload.category_id)
        if not category:
            raise NotFoundError("Category not found")

        duplicate = await self.subcategories.get_by_category_and_name(
            payload.category_id, payload.name
        )
        if duplicate:
            raise ConflictError("Subcategory name already exists in this category")

        try:
            subcategory = await self.subcategories.create(
                category_id=payload.category_id,
                name=payload.name,
                description=payload.description,
                is_active=payload.is_active,
            )
            await self.session.commit()
            return subcategory
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Subcategory name already exists in this category")

    async def get_by_id(self, subcategory_id: int) -> SubCategory:
        subcategory = await self.subcategories.get_by_id(subcategory_id)
        if not subcategory:
            raise NotFoundError("Subcategory not found")
        return subcategory

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
    ) -> list[SubCategory]:
        return await self.subcategories.get_all(
            limit=limit,
            offset=offset,
            is_active=is_active,
            sort_order=sort_order,
        )

    async def get_by_category_id(
        self,
        category_id: int,
        *,
        limit: int,
        offset: int,
        is_active: bool | None,
        sort_order: str,
    ) -> list[SubCategory]:
        category = await self.categories.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")

        return await self.subcategories.get_by_category_id(
            category_id,
            limit=limit,
            offset=offset,
            is_active=is_active,
            sort_order=sort_order,
        )

    async def update(self, subcategory_id: int, payload: SubCategoryUpdate) -> SubCategory:
        subcategory = await self.get_by_id(subcategory_id)
        data = payload.model_dump(exclude_unset=True)

        target_category_id = data.get("category_id", subcategory.category_id)
        target_name = data.get("name", subcategory.name)

        category = await self.categories.get_by_id(target_category_id)
        if not category:
            raise NotFoundError("Category not found")

        duplicate = await self.subcategories.get_by_category_and_name(
            target_category_id,
            target_name,
        )
        if duplicate and duplicate.id != subcategory.id:
            raise ConflictError("Subcategory name already exists in this category")

        try:
            updated = await self.subcategories.update(subcategory, data=data)
            await self.session.commit()
            return updated
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Subcategory name already exists in this category")

    async def delete(self, subcategory_id: int) -> None:
        subcategory = await self.get_by_id(subcategory_id)
        await self.subcategories.delete(subcategory)
        await self.session.commit()

    @staticmethod
    def serialize(subcategory: SubCategory) -> dict:
        return SubCategoryResponse.model_validate(subcategory).model_dump()
