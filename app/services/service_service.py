from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.service import Service
from app.models.user import User
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate

USER_REQUEST = "user_request"
PROVIDER_LISTING = "provider_listing"


class ServiceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ServiceRepository(session)
        self.users = UserRepository(session)

    def serialize(self, row: Service) -> dict:
        return ServiceResponse.model_validate(row).model_dump()

    async def admin_create(self, payload: ServiceCreate) -> Service:
        if payload.user_id is None:
            raise BadRequestError("user_id is required for admin create")
        kind = payload.service_kind or USER_REQUEST
        owner = await self.users.get_by_id(payload.user_id)
        if not owner:
            raise BadRequestError("Owner user not found")
        if kind == PROVIDER_LISTING and (owner.login_as or "").lower() != "provider":
            raise BadRequestError("Provider listings must be owned by a provider account")
        try:
            row = await self.repo.create(
                obj_in={
                    "title": payload.title.strip(),
                    "description": payload.description,
                    "service_kind": kind,
                    "user_id": payload.user_id,
                }
            )
            await self.session.commit()
            return row
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Could not create service")

    async def admin_get_all(
        self,
        *,
        limit: int,
        offset: int,
        sort_order: str,
    ) -> list[Service]:
        return await self.repo.get_all(
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )

    async def admin_get_by_id(self, service_id: int) -> Service:
        row = await self.repo.get_by_id(service_id)
        if not row:
            raise NotFoundError("Service not found")
        return row

    async def admin_update(self, service_id: int, payload: ServiceUpdate) -> Service:
        row = await self.admin_get_by_id(service_id)
        data = payload.model_dump(exclude_unset=True)
        if "title" in data and data["title"] is not None:
            data["title"] = str(data["title"]).strip()
        if "user_id" in data and data["user_id"] is not None:
            owner = await self.users.get_by_id(data["user_id"])
            if not owner:
                raise BadRequestError("Owner user not found")
        try:
            updated = await self.repo.update(row, data=data)
            await self.session.commit()
            return updated
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Could not update service")

    async def admin_delete(self, service_id: int) -> None:
        row = await self.admin_get_by_id(service_id)
        await self.repo.delete(row)
        await self.session.commit()

    async def user_create_request(self, user: User, payload: ServiceCreate) -> Service:
        try:
            row = await self.repo.create(
                obj_in={
                    "title": payload.title.strip(),
                    "description": payload.description,
                    "service_kind": USER_REQUEST,
                    "user_id": user.id,
                }
            )
            await self.session.commit()
            return row
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Could not create service request")

    async def user_list_visible(self, user: User) -> list[Service]:
        return await self.repo.list_for_user_discovery(user_id=user.id)

    async def user_get_visible(self, user: User, service_id: int) -> Service:
        row = await self.repo.get_visible_for_user(user_id=user.id, service_id=service_id)
        if not row:
            raise NotFoundError("Service not found")
        return row

    async def provider_create_listing(self, user: User, payload: ServiceCreate) -> Service:
        try:
            row = await self.repo.create(
                obj_in={
                    "title": payload.title.strip(),
                    "description": payload.description,
                    "service_kind": PROVIDER_LISTING,
                    "user_id": user.id,
                }
            )
            await self.session.commit()
            return row
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Could not create service")

    async def provider_list_mine(self, user: User) -> list[Service]:
        return await self.repo.list_provider_listings(provider_user_id=user.id)
