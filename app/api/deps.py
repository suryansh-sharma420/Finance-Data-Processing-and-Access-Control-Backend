from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.core.config import settings
from app.core import security

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> User:
    """Authenticates the incoming request using a Bearer token and returns the current user."""
    user_id = security.get_current_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Query user directly from DB
    from app.repositories import user_repo
    user = user_repo.get(db, id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Ensures the current user is an administrator."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user does not have enough privileges")
    return current_user
