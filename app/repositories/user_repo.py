from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get(db: Session, id: Any) -> Optional[User]:
    """Retrieves a single user by their technical ID."""
    return db.query(User).filter(User.id == id).first()

def get_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieves a single user by their email address."""
    return db.query(User).filter(User.email == email).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Returns a list of users with pagination support."""
    return db.query(User).offset(skip).limit(limit).all()

def create(db: Session, obj_in: UserCreate) -> User:
    """Creates a new user record in the database."""
    db_obj = User(
        email=obj_in.email,
        username=obj_in.username,
        hashed_password=obj_in.password, # Note: Hashed by service
        role=obj_in.role
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
    """Updates an existing user record and returns the refreshed object."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, id: int) -> Optional[User]:
    """Deletes a user account and returns the deleted object if found."""
    obj = db.query(User).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
