from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.dependencies import get_current_user
from schemas.user import UserCreate, TokenRefresh, ForgotPassword, ResetPassword
from api.controllers.auth_controller import AuthController
from schemas.base import BaseResponse
from typing import Any

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Any)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return AuthController.register(user_data, db)

@router.post("/login", response_model=Any)
def login(email: str, password: str, db: Session = Depends(get_db)):
    return AuthController.login(email, password, db)

@router.post("/refresh", response_model=Any)
def refresh_token(data: TokenRefresh):
    return AuthController.refresh(data.refresh_token)

@router.post("/forgot-password", response_model=Any)
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    return AuthController.forgot_password(data, db)

@router.post("/reset-password", response_model=Any)
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    return AuthController.reset_password(data, db)

@router.post("/logout", response_model=Any)
def logout(refresh_token: str, current_user = Depends(get_current_user)):
    return AuthController.logout(refresh_token)

