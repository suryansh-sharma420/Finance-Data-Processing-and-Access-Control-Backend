from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.record import Record
from app.schemas.record import RecordCreate, RecordUpdate

def get(db: Session, id: int) -> Optional[Record]:
    """Retrieves a single financial record by its unique ID."""
    return db.query(Record).filter(Record.id == id).first()

def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    category: Optional[str] = None, # Changed: ID to String
    user_id: Optional[int] = None
) -> List[Record]:
    """Retrieves a list of records based on applied filters and pagination."""
    query = db.query(Record)
    if type:
        query = query.filter(Record.type == type)
    if category:
        query = query.filter(Record.category == category)
    if user_id:
        query = query.filter(Record.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_with_owner(db: Session, obj_in: Dict[str, Any], user_id: int) -> Record:
    """Creates a new record and assigns it to a specific user (owner)."""
    db_obj = Record(**obj_in, user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Record, obj_in: Union[RecordUpdate, Dict[str, Any]]) -> Record:
    """Updates an existing record with new data."""
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

def remove(db: Session, id: int) -> Optional[Record]:
    """Deletes a record from the database."""
    obj = db.query(Record).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj

def get_monthly_totals_by_user(db: Session, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Groups user's records by Month (YYYY-MM) and calculates total Income and Expenses."""
    from sqlalchemy import func, case
    
    month_col = func.strftime("%Y-%m", Record.date).label("month")
    q = db.query(
        month_col,
        func.sum(case((Record.type == "Income", Record.amount), else_=0)).label("income"),
        func.sum(case((Record.type == "Expense", Record.amount), else_=0)).label("expenses")
    )
    if user_id:
        q = q.filter(Record.user_id == user_id)
        
    results = q.group_by("month").order_by("month").all()
    
    return [
        {"month": r.month, "income": float(r.income), "expenses": float(r.expenses)}
        for r in results
    ]
