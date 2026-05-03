from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import login_as as login_as_const
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAdminOut, UserCreate, UserProfileUpdate, UserPublic
from app.services.provider_profile_service import ProviderProfileService
from app.utils.user_name import display_name_from_parts


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        la = (data.login_as or login_as_const.USER).strip().lower()
        if la not in (login_as_const.USER, login_as_const.PROVIDER):
            raise BadRequestError("Invalid account type for registration")
        email_norm = str(data.email).strip().lower()
        if await self.users.get_by_email(email_norm):
            raise ConflictError("Email already registered")
        hashed = get_password_hash(data.password)
        fn = data.first_name.strip()
        ln = data.last_name.strip()
        display = display_name_from_parts(fn, ln)
        try:
            user = await self.users.create_user(
                first_name=fn,
                last_name=ln,
                name=display,
                email=email_norm,
                phone=data.phone,
                country=data.country.strip(),
                latitude=data.latitude,
                longitude=data.longitude,
                hashed_password=hashed,
                login_as=la,
                role_id=None,
            )
            if la == login_as_const.PROVIDER:
                profile_svc = ProviderProfileService(self.session)
                await profile_svc.ensure_stub_for_provider_user(user)
            await self.session.commit()
            reloaded = await self.users.get_by_id(user.id)
            if not reloaded:
                raise ConflictError("Registration failed")
            return reloaded
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Email already registered")

    async def get_by_id(self, user_id: int) -> User:
        user = await self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def list_users(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.users.list_all_with_role(skip=skip, limit=limit)

    async def list_users_for_admin(self, *, skip: int, limit: int) -> list[User]:
        capped = min(max(limit, 1), 200)
        return await self.list_users(skip=skip, limit=capped)

    async def update_profile(self, user: User, payload: UserProfileUpdate) -> User:
        patch = payload.model_dump(exclude_unset=True)
        if not patch:
            raise BadRequestError("No fields to update")
        if "first_name" in patch and patch["first_name"] is not None:
            user.first_name = str(patch["first_name"]).strip()[:100]
        if "last_name" in patch and patch["last_name"] is not None:
            user.last_name = str(patch["last_name"]).strip()[:100]
        if "first_name" in patch or "last_name" in patch:
            user.name = display_name_from_parts(user.first_name, user.last_name)
        if "country" in patch:
            user.country = str(patch["country"]).strip()[:120] if patch["country"] else None
        if "phone" in patch:
            user.phone = patch["phone"]
        if "latitude" in patch:
            user.latitude = patch["latitude"]
        if "longitude" in patch:
            user.longitude = patch["longitude"]
        await self.session.flush()
        if user.login_as == login_as_const.PROVIDER:
            profile_svc = ProviderProfileService(self.session)
            prof = await profile_svc.profiles.get_by_user_id(user.id)
            if prof:
                await profile_svc.profiles.update_by_user_id(
                    user.id,
                    profile_svc._identity_columns(user),
                )
                await self.session.flush()
        await self.session.commit()
        reloaded = await self.users.get_by_id(user.id)
        if not reloaded:
            raise NotFoundError("User not found")
        return reloaded

    @staticmethod
    def serialize_public(user: User) -> dict:
        data = UserPublic.model_validate(user).model_dump()
        if data.get("latitude") is not None:
            data["latitude"] = float(data["latitude"])
        if data.get("longitude") is not None:
            data["longitude"] = float(data["longitude"])
        return data

    @staticmethod
    def serialize_admin_rows(users: list[User]) -> list[dict]:
        return [UserAdminOut.model_validate(u).model_dump() for u in users]
