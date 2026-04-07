from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.schemas import record as record_schema
from app.services import record_service as service
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=record_schema.Record)
def create_record(record_in: record_schema.RecordCreate, db: Session = Depends(get_db), current_user = Depends(deps.get_current_user)):
    """Creates a new financial record using defined Category Enums."""
    # RBAC Enforcement: Viewers are forbidden from creation
    if current_user.role == "Viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user does not have enough privileges"
        )
    
    try:
        return service.create_record(db, obj_in=record_in, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[record_schema.Record])
def read_records(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    category: Optional[str] = None, # Changed: ID to String
    current_user = Depends(deps.get_current_user)
):
    """Lists financial records based on Enums filters."""
    # Scope check: Non-superusers only see their own records
    user_id = None if current_user.is_superuser else current_user.id
    return service.get_multi_records(db, skip=skip, limit=limit, type=type, category=category, user_id=user_id)

@router.get("/{record_id}", response_model=record_schema.Record)
def read_record_by_id(record_id: int, db: Session = Depends(get_db), current_user = Depends(deps.get_current_user)):
    """Fetches a specific record by ID."""
    record = service.get_record(db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    if not current_user.is_superuser and record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this record")
    
    return record

@router.patch("/{record_id}", response_model=record_schema.Record)
def update_record(record_id: int, record_in: record_schema.RecordUpdate, db: Session = Depends(get_db), current_user = Depends(deps.get_current_active_superuser)):
    """Modifies attributes of an existing financial entry (Admin Only)."""
    db_obj = service.get_record(db, record_id=record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Record not found")
        
    try:
        return service.update_record(db, db_obj=db_obj, obj_in=record_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int, db: Session = Depends(get_db), current_user = Depends(deps.get_current_active_superuser)):
    """Deletes a record (Admin Only)."""
    try:
        success = service.remove_record(db, record_id=record_id)
        if not success:
            raise HTTPException(status_code=404, detail="Record not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
