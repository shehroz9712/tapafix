from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id_: int) -> ModelType | None:
        result = await self.session.get(self.model, id_)
        return result

    async def create(self, *, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update_by_id(self, id_: int, data: dict[str, Any]) -> ModelType | None:
        await self.session.execute(
            update(self.model).where(self.model.id == id_).values(**data)
        )
        await self.session.flush()
        return await self.get_by_id(id_)

    async def delete_by_id(self, id_: int) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == id_))

    async def list_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
