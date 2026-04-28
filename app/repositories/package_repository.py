from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.package import Package
from app.repositories.base import BaseRepository


class PackageRepository(BaseRepository[Package]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Package)

    async def create(
        self,
        *,
        name: str,
        sort: int,
        image: str | None,
        price: float,
        duration: int,
        description: str | None,
        payment_interval: str | None,
        currency: str,
        services: int | None,
    ) -> Package:
        return await super().create(
            obj_in={
                "name": name.strip(),
                "sort": sort,
                "image": image,
                "price": price,
                "duration": duration,
                "description": description,
                "payment_interval": payment_interval,
                "currency": currency,
                "services": services,
            }
        )

    async def get_by_name(self, name: str) -> Package | None:
        stmt = select(Package).where(func.lower(Package.name) == name.strip().lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: str,
    ) -> list[Package]:
        stmt = select(Package)
        if sort_order == "asc":
            stmt = stmt.order_by(Package.sort.asc(), Package.created_at.asc())
        else:
            stmt = stmt.order_by(Package.sort.asc(), Package.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, package: Package, *, data: dict) -> Package:
        for key, value in data.items():
            setattr(package, key, value)
        await self.session.flush()
        await self.session.refresh(package)
        return package

    async def delete(self, package: Package) -> None:
        await self.session.delete(package)
        await self.session.flush()
