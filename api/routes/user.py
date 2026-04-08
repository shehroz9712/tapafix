from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db.session import get_db
from core.dependencies import get_current_user, get_admin_user
from services.user import UserService
from schemas.user import UserOut, UserResponse
from api.controllers.base_controller import BaseController
from utils.pagination import Pagination
from schemas.base import BaseResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseController.success(user)

@router.get("/", response_model=BaseResponse[Pagination[UserOut]])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    page: int = 1,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    pagination = UserService.get_all(db, skip, limit, page)
    return BaseController.success(pagination)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str, 
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = UserService.update(db, user_id, name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseController.success(user, "User updated")

