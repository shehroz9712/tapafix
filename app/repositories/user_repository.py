from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import login_as as login_as_const
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(func.lower(User.email) == email.strip().lower())
            .options(joinedload(User.assigned_role))
            .order_by(User.id.desc())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def get_by_provider(self, provider: str, provider_id: str) -> User | None:
        stmt = (
            select(User)
            .where(User.provider == provider, User.provider_id == provider_id)
            .options(joinedload(User.assigned_role))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, id_: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == id_)
            .options(joinedload(User.assigned_role))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_user(
        self,
        *,
        name: str,
        email: str,
        phone: str | None,
        hashed_password: str,
        login_as: str = login_as_const.USER,
        role_id: int | None = None,
        provider: str = "email",
        provider_id: str | None = None,
        avatar_url: str | None = None,
        is_verified: bool = False,
    ) -> User:
        return await self.create(
            obj_in={
                "name": name,
                "email": email,
                "phone": phone,
                "hashed_password": hashed_password,
                "login_as": login_as,
                "role_id": role_id,
                "provider": provider,
                "provider_id": provider_id,
                "avatar_url": avatar_url,
                "is_active": True,
                "is_verified": is_verified,
            }
        )

    async def create_social_user(
        self,
        *,
        name: str,
        email: str,
        hashed_password: str,
        provider: str,
        provider_id: str,
        avatar_url: str | None,
        is_verified: bool,
        login_as: str = login_as_const.USER,
    ) -> User:
        return await self.create_user(
            name=name,
            email=email,
            phone=None,
            hashed_password=hashed_password,
            login_as=login_as,
            role_id=None,
            provider=provider,
            provider_id=provider_id,
            avatar_url=avatar_url,
            is_verified=is_verified,
        )

    async def merge_oauth_identity(
        self,
        user_id: int,
        *,
        provider: str,
        provider_id: str,
        name: str | None,
        avatar_url: str | None,
        email: str | None,
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.provider = provider
        user.provider_id = provider_id
        user.is_verified = True
        if avatar_url:
            user.avatar_url = avatar_url
        if name:
            user.name = name[:200]
        if email:
            el = email.strip().lower()
            if user.email.lower() != el:
                user.email = el
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_password(self, user_id: int, hashed_password: str) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.hashed_password = hashed_password
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def promote_to_admin(self, user_id: int, role_id: int) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.role_id = role_id
        user.login_as = login_as_const.ADMIN
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def assign_account_role(
        self, user_id: int, *, login_as: str, role_id: int | None
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.login_as = login_as
        user.role_id = role_id
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_all_with_role(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[User]:
        stmt = (
            select(User)
            .options(joinedload(User.assigned_role))
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
