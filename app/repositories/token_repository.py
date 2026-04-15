from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken
from app.models.revoked_refresh_token import RevokedRefreshToken
from app.repositories.base import BaseRepository


class TokenRepository(BaseRepository[PasswordResetToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PasswordResetToken)

    async def create_reset_token(
        self, *, user_id: int, token: str, expires_at: datetime
    ) -> PasswordResetToken:
        return await self.create(
            obj_in={
                "user_id": user_id,
                "token": token,
                "expires_at": expires_at,
            }
        )

    async def get_valid_reset_token(self, token: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if not row:
            return None
        if row.expires_at < datetime.now(timezone.utc):
            return None
        return row

    async def delete_for_user(self, user_id: int) -> None:
        await self.session.execute(
            delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        )

    async def delete_token(self, token_id: int) -> None:
        await self.delete_by_id(token_id)


class RefreshBlacklistRepository(BaseRepository[RevokedRefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RevokedRefreshToken)

    async def is_revoked(self, jti: str) -> bool:
        stmt = select(RevokedRefreshToken).where(RevokedRefreshToken.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def revoke(self, *, jti: str, expires_at: datetime) -> None:
        if await self.is_revoked(jti):
            return
        self.session.add(RevokedRefreshToken(jti=jti, expires_at=expires_at))
        await self.session.flush()
