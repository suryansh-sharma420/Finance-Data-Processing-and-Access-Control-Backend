from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from app.core import security
from app.repositories import user_repo as repo
from app.schemas.user import UserCreate, UserUpdate
from app.db.models.user import User

def create_user(db: Session, obj_in: UserCreate) -> User:
    """Handles hashing and creation of a new user."""
    # Safety Check: Email existence
    existing_user = repo.get_by_email(db, email=obj_in.email)
    if existing_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_pwd = security.get_password_hash(obj_in.password)
    obj_in.password = hashed_pwd
    return repo.create(db, obj_in=obj_in)

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Orchestrates single-user retrieval."""
    return repo.get(db, id=user_id)

def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    """Verifies credentials."""
    user = repo.get_by_email(db, email=email)
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user

def get_multi_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Orchestrates paginated user retrieval."""
    return repo.get_multi(db, skip=skip, limit=limit)

def update_user(db: Session, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
    """Orchestrates user updates including selective hashing of changed passwords."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    if update_data.get("password"):
        update_data["hashed_password"] = security.get_password_hash(update_data["password"])
        del update_data["password"]

    # Important: Guarantee the repo call's result is returned
    result = repo.update(db, db_obj=db_obj, obj_in=update_data)
    return result

def delete_user(db: Session, user_id: int) -> Optional[User]:
    """Orchestrates user deletion."""
    return repo.remove(db, id=user_id)
