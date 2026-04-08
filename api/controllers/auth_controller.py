from schemas.user import UserCreate, TokenRefresh, ForgotPassword, ResetPassword, TokensResponse, UserResponse
from services.auth import AuthService
from api.controllers.base_controller import BaseController
from schemas.user import UserOut, Token
from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import get_db

class AuthController:
    @staticmethod
    def register(user_create: UserCreate, db = Depends(get_db)) -> TokensResponse:
        try:
            user = AuthService.register(db, user_create)
            if not user:
                return BaseController.error("Registration failed")
            tokens = AuthService.login(db, user.email, user_create.password)
            return BaseController.success(tokens, "User registered successfully")
        except ValueError as e:
            return BaseController.error(str(e))

    @staticmethod
    def login(email: str, password: str, db = Depends(get_db)) -> TokensResponse:
        tokens = AuthService.login(db, email, password)
        if not tokens:
            return BaseController.error("Invalid credentials")
        return BaseController.success(tokens, "Login successful")

    @staticmethod
    def refresh(refresh_token: str) -> TokensResponse:
        tokens = AuthService.refresh(refresh_token)
        if not tokens:
            return BaseController.error("Invalid refresh token")
        return BaseController.success(tokens, "Tokens refreshed")

    @staticmethod
    def forgot_password(data: ForgotPassword, db = Depends(get_db)) -> BaseResponse[str]:
        try:
            token = AuthService.forgot_password(db, data)
            return BaseController.success(token, "Reset token sent to email")
        except Exception as e:
            return BaseController.error("Failed to send reset email")

    @staticmethod
    def reset_password(data: ResetPassword, db = Depends(get_db)) -> BaseResponse[None]:
        success = AuthService.reset_password(db, data)
        if success:
            return BaseController.success(None, "Password reset successful")
        return BaseController.error("Invalid or expired token")

    @staticmethod
    def logout(refresh_token: str) -> BaseResponse[None]:
        AuthService.logout(refresh_token)
        return BaseController.success(None, "Logged out successfully")

