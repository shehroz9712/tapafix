from typing import Generator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from db.session import SessionLocal
from core.security import verify_token, TokenData
from core.config import settings

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> TokenData:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_token(token)
    if not token_data or not token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

async def get_admin_user(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)) -> TokenData:
    # Add role check here when roles implemented
    if "admin" not in current_user.scopes:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

