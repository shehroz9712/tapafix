from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import login_as as login_as_const
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAdminOut, UserCreate, UserPublic


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        la = (data.login_as or login_as_const.USER).strip().lower()
        if la not in (login_as_const.USER, login_as_const.PROVIDER):
            raise BadRequestError("Invalid account type for registration")
        hashed = get_password_hash(data.password)
        try:
            user = await self.users.create_user(
                name=data.name,
                email=str(data.email).lower(),
                phone=data.phone,
                hashed_password=hashed,
                login_as=la,
                role_id=None,
            )
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

    @staticmethod
    def serialize_public(user: User) -> dict:
        return UserPublic.model_validate(user).model_dump()

    @staticmethod
    def serialize_admin_rows(users: list[User]) -> list[dict]:
        return [UserAdminOut.model_validate(u).model_dump() for u in users]
