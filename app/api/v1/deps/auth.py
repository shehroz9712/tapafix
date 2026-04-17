from collections.abc import Iterable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.db import get_db
from app.core.security import decode_token, parse_access_payload
from app.exceptions import ForbiddenError, UnauthorizedError
from app.models import login_as as login_as_const
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user: User
    token_permissions: list[str]
    token_role: str | None
    token_login_as: str | None


async def get_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthContext:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Not authenticated")
    raw = decode_token(credentials.credentials)
    payload = parse_access_payload(credentials.credentials)
    if not payload or not payload.sub:
        raise UnauthorizedError("Invalid or expired token")
    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise UnauthorizedError("Invalid or expired token")

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("Invalid or expired token")
    if raw is not None and "login_as" in raw:
        token_la = str(raw["login_as"]).strip().lower()
        if token_la != user.login_as:
            raise UnauthorizedError("Invalid or expired token")
    return AuthContext(
        user=user,
        token_permissions=payload.permissions,
        token_role=payload.role,
        token_login_as=payload.login_as,
    )


async def get_current_user(
    ctx: Annotated[AuthContext, Depends(get_auth_context)],
) -> User:
    return ctx.user


def RequirePermission(permission_name: str):
    async def _check(
        ctx: Annotated[AuthContext, Depends(get_auth_context)],
        session: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        if ctx.user.login_as != login_as_const.ADMIN:
            raise ForbiddenError("Permission denied")
        svc = PermissionService(session)
        allowed = await svc.user_has_permission(
            user=ctx.user,
            permission_name=permission_name,
            jwt_permissions=ctx.token_permissions,
        )
        if not allowed:
            raise ForbiddenError("Permission denied")

    return Depends(_check)


def require_admin():
    return require_role(login_as_const.ADMIN, "Administrator access required")


def require_user():
    return require_role(login_as_const.USER, "Customer access required")


def require_provider():
    return require_role(login_as_const.PROVIDER, "Provider access required")


def require_role(expected_role: str | Iterable[str], message: str | None = None):
    async def _check(
        ctx: Annotated[AuthContext, Depends(get_auth_context)],
    ) -> None:
        if isinstance(expected_role, str):
            allowed_roles = {expected_role.strip().lower()}
        else:
            allowed_roles = {str(role).strip().lower() for role in expected_role}
        if not allowed_roles:
            raise ForbiddenError("Permission denied")
        token_role = (ctx.token_role or "").strip().lower()
        user_role = (ctx.user.login_as or "").strip().lower()
        if token_role and token_role != user_role:
            raise UnauthorizedError("Invalid token role")
        if user_role not in allowed_roles:
            raise ForbiddenError(message or "Permission denied")

    return Depends(_check)
