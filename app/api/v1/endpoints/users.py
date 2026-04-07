from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas import user as user_schema
from app.services import user_service as service
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: user_schema.UserCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_superuser)
):
    """Registers a new user into the system (Requires Administrator privileges)."""
    user = service.create_user(db, obj_in=user_in)
    if not user:
        raise HTTPException(status_code=400, detail="Registration failed (User already exists)")
    return user

@router.get("/", response_model=List[user_schema.User])
def read_users(db: Session = Depends(get_db), current_user = Depends(deps.get_current_active_superuser)):
    """Lists all registered system users (Requires Administrator privileges)."""
    return service.get_multi_users(db)

@router.get("/{user_id}", response_model=user_schema.User)
def read_user_by_id(user_id: int, db: Session = Depends(get_db), current_user = Depends(deps.get_current_user)):
    """Fetches a specific user profile (Self or Admin only)."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden: You can only view your own profile")
    
    user = service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=user_schema.User)
def update_user(user_id: int, user_in: user_schema.UserUpdate, db: Session = Depends(get_db), current_user = Depends(deps.get_current_user)):
    """Applies partial updates to an existing user profile (Self or Admin only)."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden: You can only update your own profile")
        
    db_obj = service.get_user(db, user_id=user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
        
    updated_user = service.update_user(db, db_obj=db_obj, obj_in=user_in)
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(deps.get_current_user)):
    """Removes a user permanently (Self or Admin only)."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden: You can only delete your own account")
    
    success = service.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deletion target not found")
    return None
