from typing import Literal

from pydantic import BaseModel, EmailStr, Field

LoginAsOption = Literal["user", "provider", "admin"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)
    login_as: LoginAsOption = Field(
        ...,
        description="Must match the account profile stored for this user.",
    )


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10, max_length=256)
    password: str = Field(..., min_length=8, max_length=128)


class LogoutRequest(BaseModel):
    refresh_token: str


class SocialLoginRequest(BaseModel):
    provider: Literal["google", "facebook", "apple"]
    token: str = Field(..., min_length=10, max_length=16000)


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=8)
