from sqlalchemy.orm import Session
from db.models.user import User
from schemas.user import UserCreate, UserOut
from core.security import get_password_hash
from typing import Optional, List
from utils.pagination import paginate, Pagination

class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, page: int = 1) -> Pagination[UserOut]:
        users = db.query(User).offset(skip).limit(limit).all()
        return paginate(users, page, limit)

    @staticmethod
    def create(db: Session, user_create: UserCreate) -> User:
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            name=user_create.name,
            email=user_create.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(db: Session, user_id: str, name: Optional[str] = None) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if name:
                user.name = name
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

