from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime
from app.repositories import record_repo as repo
from app.schemas.record import RecordCreate, RecordUpdate
from app.db.models.record import Record

def create_record(db: Session, obj_in: RecordCreate, user_id: int) -> Record:
    """Orchestrates the creation of a financial record (Enum based)."""
    # Validation for positive amount is handled by Pydantic.
    # Validation for category is handled by Pydantic Literal.
    obj_data = obj_in.model_dump()
    return repo.create_with_owner(db, obj_in=obj_data, user_id=user_id)
    
def get_record(db: Session, record_id: int) -> Optional[Record]:
    """Retrieves a single financial record by its unique ID."""
    return repo.get(db, id=record_id)

def get_multi_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    category: Optional[str] = None, # Changed: ID to String
    user_id: Optional[int] = None
) -> List[Record]:
    """Retrieves records based on scope and filters."""
    return repo.get_multi(db, skip=skip, limit=limit, type=type, category=category, user_id=user_id)
    
def update_record(db: Session, db_obj: Record, obj_in: Union[RecordUpdate, Dict[str, Any]]) -> Record:
    """Updates an existing record, ensuring logic consistency."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Amount validation handled by Pydantic 'gt=0' in RecordUpdate.
    return repo.update(db, db_obj=db_obj, obj_in=update_data)

def remove_record(db: Session, record_id: int) -> Record:
    """Deletes a record after validating its existence."""
    record = repo.get(db, id=record_id)
    if not record:
        raise ValueError("Record not found")
    
    return repo.remove(db, id=record_id)
