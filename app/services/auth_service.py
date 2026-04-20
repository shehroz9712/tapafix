from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    parse_refresh_payload,
    verify_password,
)
from app.exceptions import BadRequestError, UnauthorizedError
from app.models import login_as as login_as_const
from app.models.user import User
from app.repositories.token_repository import RefreshBlacklistRepository, TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, ResetPasswordRequest, TokenPair
from app.schemas.user import UserCreate
from app.services.permission_service import PermissionService
from app.services.social_auth_service import SocialAuthService
from app.utils.email import send_password_reset_email


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.tokens = TokenRepository(session)
        self.blacklist = RefreshBlacklistRepository(session)

    async def register(self, data: UserCreate) -> tuple[User, TokenPair]:
        from app.services.user_service import UserService

        user_service = UserService(self.session)
        user = await user_service.register(data)
        tokens = await self._issue_tokens(user)
        return user, tokens

    async def login(self, data: LoginRequest) -> TokenPair:
        user = await self.users.get_by_email(str(data.email).lower())
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")
        if data.login_as.strip().lower() != user.login_as:
            raise UnauthorizedError("Invalid credentials")
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = parse_refresh_payload(refresh_token)
        if not payload or not payload.jti:
            raise UnauthorizedError("Invalid or expired refresh token")
        if await self.blacklist.is_revoked(payload.jti):
            raise UnauthorizedError("Refresh token has been revoked")

        exp_ts = self._jwt_exp(refresh_token)
        if not exp_ts:
            raise UnauthorizedError("Invalid refresh token")

        try:
            user_id = int(payload.sub)
        except (TypeError, ValueError):
            raise UnauthorizedError("Invalid credentials")

        user = await self.users.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid credentials")

        await self.blacklist.revoke(jti=payload.jti, expires_at=exp_ts)
        tokens = await self._issue_tokens(user)
        await self.session.commit()
        return tokens

    async def forgot_password(self, data: ForgotPasswordRequest) -> None:
        email = str(data.email).lower()
        user = await self.users.get_by_email(email)
        if not user:
            logger.warning("Password reset requested for unknown email")
            return
        await self.tokens.delete_for_user(user.id)
        raw = secrets.token_urlsafe(48)
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
        )
        await self.tokens.create_reset_token(user_id=user.id, token=raw, expires_at=expires)
        await self.session.commit()
        await send_password_reset_email(to_email=user.email, token=raw)

    async def reset_password(self, data: ResetPasswordRequest) -> None:
        row = await self.tokens.get_valid_reset_token(data.token)
        if not row:
            raise BadRequestError("Invalid or expired reset token")
        user = await self.users.get_by_id(row.user_id)
        if not user:
            raise BadRequestError("Invalid or expired reset token")
        user.hashed_password = get_password_hash(data.password)
        await self.tokens.delete_token(row.id)
        await self.session.commit()
        await self.session.refresh(user)

    async def logout(self, refresh_token: str) -> None:
        payload = parse_refresh_payload(refresh_token)
        if not payload or not payload.jti:
            raise UnauthorizedError("Invalid refresh token")
        exp_ts = self._jwt_exp(refresh_token)
        if not exp_ts:
            raise UnauthorizedError("Invalid refresh token")
        await self.blacklist.revoke(jti=payload.jti, expires_at=exp_ts)
        await self.session.commit()

    async def social_login(self, provider: str, token: str) -> TokenPair:
        social = SocialAuthService()
        profile = await social.verify_and_profile(provider, token)
        effective_email = (
            profile.email.lower()
            if profile.email
            else SocialAuthService.placeholder_email(profile.provider, profile.provider_id)
        )

        by_oauth = await self.users.get_by_provider(profile.provider, profile.provider_id)
        if by_oauth:
            if not by_oauth.is_active:
                raise UnauthorizedError("Account is inactive")
            return await self._issue_tokens(by_oauth)

        by_email = await self.users.get_by_email(effective_email)
        if by_email:
            if not by_email.is_active:
                raise UnauthorizedError("Account is inactive")
            try:
                merged = await self.users.merge_oauth_identity(
                    by_email.id,
                    provider=profile.provider,
                    provider_id=profile.provider_id,
                    name=profile.name,
                    avatar_url=profile.avatar_url,
                    email=profile.email,
                )
                if not merged:
                    raise UnauthorizedError("Could not link account")
                await self.session.commit()
            except IntegrityError:
                await self.session.rollback()
                raise BadRequestError("Cannot link account due to email conflict")
            reloaded = await self.users.get_by_id(by_email.id)
            if not reloaded:
                raise UnauthorizedError("Could not link account")
            return await self._issue_tokens(reloaded)

        rnd = get_password_hash(secrets.token_urlsafe(48))
        try:
            user = await self.users.create_social_user(
                name=profile.name,
                email=effective_email,
                hashed_password=rnd,
                provider=profile.provider,
                provider_id=profile.provider_id,
                avatar_url=profile.avatar_url,
                is_verified=bool(profile.email),
                login_as=login_as_const.USER,
            )
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            existing = await self.users.get_by_provider(profile.provider, profile.provider_id)
            if existing and existing.is_active:
                return await self._issue_tokens(existing)
            raise BadRequestError("Could not create account") from None

        reloaded = await self.users.get_by_id(user.id)
        if not reloaded:
            raise UnauthorizedError("Registration failed")
        return await self._issue_tokens(reloaded)

    async def _issue_tokens(self, user: User) -> TokenPair:
        perm_svc = PermissionService(self.session)
        if user.login_as == login_as_const.ADMIN:
            perms = await perm_svc.permission_names_for_role(user.role_id)
            access = create_access_token(
                subject=user.id,
                login_as=user.login_as,
                role_name=user.role_name,
                permissions=perms,
            )
        else:
            access = create_access_token(subject=user.id, login_as=user.login_as)
        refresh, _jti = create_refresh_token(subject=user.id)
        return TokenPair(access_token=access, refresh_token=refresh)

    def _jwt_exp(self, token: str) -> datetime | None:
        try:
            payload = jwt.get_unverified_claims(token)
            exp = payload.get("exp")
            if exp is None:
                return None
            return datetime.fromtimestamp(int(exp), tz=timezone.utc)
        except Exception:
            return None
