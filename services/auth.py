from sqlalchemy.orm import Session
from db.models.user import User
from schemas.user import UserCreate, Token, TokenRefresh, ForgotPassword, ResetPassword
from core.security import verify_password, create_access_token, create_refresh_token, create_reset_token, verify_token
from services.user import UserService
from logger import logger
from typing import Optional
import secrets

class AuthService:
    @staticmethod
    def register(db: Session, user_create: UserCreate) -> Optional[User]:
        db_user = UserService.get_by_email(db, user_create.email)
        if db_user:
            raise ValueError("Email already registered")
        return UserService.create(db, user_create)

    @staticmethod
    def login(db: Session, email: str, password: str) -> Optional[Token]:
        user = UserService.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise ValueError("Inactive user")
        access_token = create_access_token(str(user.id), [user.role])
        refresh_token = create_refresh_token(str(user.id))
        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh(refresh_token: str) -> Optional[Token]:
        token_data = verify_token(refresh_token, "refresh")
        if not token_data or not token_data.sub:
            return None
        access_token = create_access_token(token_data.sub, token_data.scopes)
        new_refresh = create_refresh_token(token_data.sub)
        return Token(access_token=access_token, refresh_token=new_refresh)

    @staticmethod
    def forgot_password(db: Session, data: ForgotPassword) -> str:
        user = UserService.get_by_email(db, data.email)
        if not user:
            logger.warning(f"Forgot password requested for non-existent email: {data.email}")
        reset_token = create_reset_token(data.email)
        # TODO: Send email with reset_token
        logger.info(f"Reset token generated for {data.email}")
        return reset_token

    @staticmethod
    def reset_password(db: Session, data: ResetPassword) -> bool:
        token_data = verify_token(data.token, "reset")
        if not token_data or not token_data.sub:
            return False
        user = UserService.get_by_email(db, token_data.sub)
        if user:
            user.hashed_password = get_password_hash(data.password)
            db.commit()
            db.refresh(user)
            logger.info(f"Password reset for user {user.id}")
            return True
        return False

    @staticmethod
    def logout(refresh_token: str):
        # In production, add to blacklist
        logger.info("User logged out")
        return True

