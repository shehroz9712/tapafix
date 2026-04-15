from datetime import datetime, timedelta, timezone
import base64
import hashlib
from typing import Any, Optional
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models import login_as as login_as_const


class TokenPayload(BaseModel):
    sub: str
    user_id: Optional[str] = None
    login_as: Optional[str] = None
    role: Optional[str] = None
    permissions: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    token_type: Optional[str] = None
    jti: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("bcrypt_sha256$"):
        digest = _bcrypt_sha256_digest(plain_password)
        stored = hashed_password[len("bcrypt_sha256$") :].encode("utf-8")
        return bcrypt.checkpw(digest, stored)
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    digest = _bcrypt_sha256_digest(password)
    hashed = bcrypt.hashpw(digest, bcrypt.gensalt(rounds=12)).decode("utf-8")
    return f"bcrypt_sha256${hashed}"


def _bcrypt_sha256_digest(password: str) -> bytes:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def _encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    *,
    subject: int,
    login_as: str,
    role_name: str | None = None,
    permissions: list[str] | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    sid = str(subject)
    payload: dict[str, Any] = {
        "exp": expire,
        "sub": sid,
        "user_id": sid,
        "login_as": login_as,
        "type": "access",
    }
    if login_as == login_as_const.ADMIN:
        payload["role"] = role_name or ""
        payload["permissions"] = list(permissions or [])
    return _encode(payload)


def create_refresh_token(*, subject: int) -> tuple[str, str]:
    jti = str(uuid4())
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "jti": jti,
    }
    return _encode(payload), jti


def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        return None


def parse_access_payload(token: str) -> Optional[TokenPayload]:
    payload = decode_token(token)
    if not payload or payload.get("type") not in (None, "access"):
        return None
    if payload.get("type") == "refresh":
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    raw_perms = payload.get("permissions")
    permissions = [str(p) for p in raw_perms] if isinstance(raw_perms, list) else []
    scopes = payload.get("scopes") or []
    if not isinstance(scopes, list):
        scopes = []
    role = str(payload.get("role")) if payload.get("role") is not None else None
    user_id = str(payload.get("user_id")) if payload.get("user_id") is not None else None
    login_as = payload.get("login_as")
    if login_as is not None:
        login_as = str(login_as)
    elif role is not None and role.upper() == "ADMIN":
        login_as = login_as_const.ADMIN
    return TokenPayload(
        sub=str(sub),
        user_id=user_id or str(sub),
        login_as=login_as,
        role=role,
        permissions=permissions,
        scopes=[str(s) for s in scopes],
        token_type="access",
        jti=payload.get("jti"),
    )


def parse_refresh_payload(token: str) -> Optional[TokenPayload]:
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return None
    sub = payload.get("sub")
    jti = payload.get("jti")
    if not sub or not jti:
        return None
    return TokenPayload(
        sub=str(sub),
        user_id=str(sub),
        permissions=[],
        scopes=[],
        token_type="refresh",
        jti=str(jti),
    )
