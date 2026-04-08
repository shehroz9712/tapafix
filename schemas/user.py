from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from schemas.base import BaseResponse

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class ResetPassword(BaseModel):
    token: str
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class UserResponse(BaseResponse[UserOut]):
    pass

class TokensResponse(BaseResponse[Token]):
    pass

