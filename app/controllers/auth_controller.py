from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    ResetPasswordRequest,
    SocialLoginRequest,
    VerifyEmailRequest,
)
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


class AuthController(BaseController):
    def __init__(self, service: AuthService):
        self._service = service

    async def register(self, payload: UserCreate) -> JSONResponse:
        await self._service.register(payload)
        return self.respond_success(None, "OTP sent to your email")

    async def login(self, payload: LoginRequest) -> JSONResponse:
        tokens = await self._service.login(payload)
        return self.respond_success(tokens.model_dump(), "Login successful")

    async def refresh(self, payload: RefreshRequest) -> JSONResponse:
        tokens = await self._service.refresh(payload.refresh_token)
        return self.respond_success(tokens.model_dump(), "Tokens refreshed")

    async def forgot_password(self, payload: ForgotPasswordRequest) -> JSONResponse:
        await self._service.forgot_password(payload)
        return self.respond_success(
            None,
            "If the email exists, reset instructions have been sent.",
        )

    async def reset_password(self, payload: ResetPasswordRequest) -> JSONResponse:
        await self._service.reset_password(payload)
        return self.respond_success(None, "Password reset successful")

    async def logout(self, payload: LogoutRequest) -> JSONResponse:
        await self._service.logout(payload.refresh_token)
        return self.respond_success(None, "Logged out successfully")

    async def social_login(self, payload: SocialLoginRequest) -> JSONResponse:
        tokens = await self._service.social_login(payload.provider, payload.token)
        return self.respond_success(tokens.model_dump(), "Social login successful")

    async def verify_email(self, payload: VerifyEmailRequest) -> JSONResponse:
        await self._service.verify_email(payload)
        return self.respond_success(None, "Email verified successfully")
