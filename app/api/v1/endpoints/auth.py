from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.services import user_service as service
from app.db.session import get_db
from app.schemas.user import User, Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticates a user and returns a JWT access token."""
    user = service.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = security.create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(deps.get_current_user)):
    """Retrieves the profile of the currently authenticated user."""
    return current_user
