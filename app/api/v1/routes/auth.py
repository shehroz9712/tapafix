from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.controllers import get_auth_controller
from app.controllers.auth_controller import AuthController
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

router = APIRouter()


@router.post("/register")
async def register(
    payload: UserCreate,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.register(payload)


@router.post("/login")
async def login(
    payload: LoginRequest,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.login(payload)


@router.post("/refresh")
async def refresh(
    payload: RefreshRequest,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.refresh(payload)


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.forgot_password(payload)


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.reset_password(payload)


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.logout(payload)


@router.post("/social-login")
async def social_login(
    payload: SocialLoginRequest,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.social_login(payload)


@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest,
    controller: Annotated[AuthController, Depends(get_auth_controller)],
):
    return await controller.verify_email(payload)
