from fastapi import HTTPException, status
from app.db.models.user import User

def check_permission_viewer(user: User):
    """Verifies that the user has at least Viewer level access."""
    if user.role not in ["Viewer", "Analyst", "Admin"]:
        raise HTTPException(status_code=403, detail="Viewer access required")

def check_permission_analyst(user: User):
    """Verifies that the user has at least Analyst level access."""
    if user.role not in ["Analyst", "Admin"]:
        raise HTTPException(status_code=403, detail="Analyst access required")

def check_permission_admin(user: User):
    """Verifies that the user has full Administrative access."""
    if user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")

def check_record_ownership(user: User, record_owner_id: int):
    """Ensures a user only accesses their own records, unless they are an Admin."""
    if user.id != record_owner_id and user.role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this record")
