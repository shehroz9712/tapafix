"""Verify OAuth tokens with Google, Facebook, and Apple (production paths)."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass

import httpx
import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jwt import PyJWKClient

from app.core.config import settings
from app.core.logger import logger
from app.exceptions import BadRequestError, UnauthorizedError
from app.models import oauth_provider as oauth

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"


@dataclass(frozen=True)
class SocialProfile:
    provider: str
    provider_id: str
    email: str | None
    name: str
    avatar_url: str | None


class SocialAuthService:
    """Stateless token verification (no DB)."""

    @staticmethod
    def placeholder_email(provider: str, provider_id: str) -> str:
        digest = hashlib.sha256(f"{provider}:{provider_id}".encode()).hexdigest()[:48]
        return f"oauth.{provider}.{digest}@id.noemail.local"

    async def verify_and_profile(self, provider: str, token: str) -> SocialProfile:
        p = provider.strip().lower()
        if p == oauth.GOOGLE:
            return await self.verify_google_token(token)
        if p == oauth.FACEBOOK:
            return await self.verify_facebook_token(token)
        if p == oauth.APPLE:
            return await self.verify_apple_token(token)
        raise BadRequestError("Unsupported provider")

    async def verify_google_token(self, token: str) -> SocialProfile:
        if not settings.GOOGLE_CLIENT_ID:
            raise BadRequestError("Google OAuth is not configured")

        def _verify() -> dict:
            return google_id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )

        try:
            info = await asyncio.to_thread(_verify)
        except ValueError as exc:
            raise UnauthorizedError("Invalid or expired Google token") from exc

        sub = info.get("sub")
        if not sub:
            raise UnauthorizedError("Invalid Google token")
        email = info.get("email")
        name = (info.get("name") or "User")[:200]
        picture = info.get("picture")
        avatar = str(picture)[:2048] if picture else None
        return SocialProfile(
            provider=oauth.GOOGLE,
            provider_id=str(sub),
            email=str(email).lower() if email else None,
            name=name,
            avatar_url=avatar,
        )

    async def verify_facebook_token(self, token: str) -> SocialProfile:
        if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_APP_SECRET:
            raise BadRequestError("Facebook OAuth is not configured")

        app_access = f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            dbg = await client.get(
                "https://graph.facebook.com/debug_token",
                params={
                    "input_token": token,
                    "access_token": app_access,
                },
            )
            try:
                dbg.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.warning("Facebook debug_token HTTP error: %s", exc)
                raise UnauthorizedError("Invalid Facebook token") from exc

            body = dbg.json()
            data = body.get("data") or {}
            if not data.get("is_valid"):
                raise UnauthorizedError("Invalid Facebook token")
            if str(data.get("app_id")) != str(settings.FACEBOOK_APP_ID):
                raise UnauthorizedError("Invalid Facebook token")
            uid = data.get("user_id")
            if not uid:
                raise UnauthorizedError("Invalid Facebook token")

            pr = await client.get(
                f"https://graph.facebook.com/v21.0/{uid}",
                params={
                    "fields": "id,email,name,picture.type(large)",
                    "access_token": token,
                },
            )
            try:
                pr.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.warning("Facebook profile HTTP error: %s", exc)
                raise UnauthorizedError("Invalid Facebook token") from exc

            prof = pr.json()
            email = prof.get("email")
            name = (prof.get("name") or "User")[:200]
            avatar = _facebook_picture_url(prof.get("picture"))

            return SocialProfile(
                provider=oauth.FACEBOOK,
                provider_id=str(prof.get("id") or uid),
                email=str(email).lower() if email else None,
                name=name,
                avatar_url=avatar,
            )

    async def verify_apple_token(self, token: str) -> SocialProfile:
        if not settings.APPLE_CLIENT_ID:
            raise BadRequestError("Apple Sign In is not configured")

        try:
            jwks_client = PyJWKClient(APPLE_JWKS_URL)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.APPLE_CLIENT_ID,
                issuer=APPLE_ISSUER,
                leeway=120,
                options={"require": ["exp", "sub"]},
            )
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired Apple token") from exc

        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedError("Invalid Apple token")
        email = payload.get("email")
        raw_name = payload.get("name")
        if isinstance(raw_name, str) and raw_name.strip():
            name = raw_name.strip()[:200]
        elif isinstance(email, str) and email:
            name = email.split("@", 1)[0][:200]
        else:
            name = "User"
        return SocialProfile(
            provider=oauth.APPLE,
            provider_id=str(sub),
            email=str(email).lower() if email else None,
            name=name,
            avatar_url=None,
        )


def _facebook_picture_url(picture: object) -> str | None:
    if picture is None:
        return None
    if isinstance(picture, str):
        return picture[:2048]
    if isinstance(picture, dict):
        data = picture.get("data")
        if isinstance(data, dict) and data.get("url"):
            return str(data["url"])[:2048]
        if picture.get("url"):
            return str(picture["url"])[:2048]
    return None
