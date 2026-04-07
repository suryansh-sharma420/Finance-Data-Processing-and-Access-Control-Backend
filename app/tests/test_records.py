from fastapi import status
from sqlalchemy.orm import Session
from app.core import security
from app.db.models.user import User
from app.db.models.record import Record

def test_create_financial_record_success_as_admin(db: Session, client):
    """Verifies that an admin user can successfully create a record with Enum Category."""
    # 1. Setup Admin
    email = "admin_test@zorvyn.com"
    hashed_pwd = security.get_password_hash("password123")
    admin = User(email=email, hashed_password=hashed_pwd, username="admin_tester", role="Admin", is_active=True)
    db.add(admin)
    db.commit()
    
    token = security.create_access_token(subject=admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. POST /api/v1/records/ with String Category
    payload = {
        "amount": 250.75,
        "type": "Income",
        "category": "Salary", # String Enum
        "description": "Admin test record"
    }
    response = client.post("/api/v1/records/", json=payload, headers=headers)
    
    # 3. Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["amount"] == 250.75
    assert data["category"] == "Salary"
    assert data["user_id"] == admin.id

def test_rbac_viewer_failure_to_create(db: Session, client):
    """Verifies that a Viewer user is forbidden from creating records."""
    # 1. Setup Viewer
    email = "viewer_test@zorvyn.com"
    hashed_pwd = security.get_password_hash("password123")
    viewer = User(email=email, hashed_password=hashed_pwd, username="viewer_tester", role="Viewer", is_active=True)
    db.add(viewer)
    db.commit()
    
    token = security.create_access_token(subject=viewer.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. POST /api/v1/records/
    payload = {"amount": 100.0, "type": "Income", "category": "Salary", "description": "Failure test record"}
    response = client.post("/api/v1/records/", json=payload, headers=headers)
    
    # 3. Assertions
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_read_dashboard_summary_accuracy(db: Session, client):
    """Verifies dashboard aggregates metrics based on String Categories."""
    # 1. Setup Records
    user = User(email="summary@test.com", username="summary_user", hashed_password="...", role="Viewer")
    db.add(user)
    db.commit()
    
    # Add one income (500) and one expense (200)
    db.add(Record(amount=500.0, type="Income", user_id=user.id, category="Salary", description="Bonus"))
    db.add(Record(amount=200.0, type="Expense", user_id=user.id, category="Food", description="Dinner"))
    db.commit()
    
    token = security.create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. GET /api/v1/dashboard/summary
    response = client.get("/api/v1/dashboard/summary", headers=headers)
    
    # 3. Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_income"] == 500.0
    assert data["total_expenses"] == 200.0
    assert data["net_balance"] == 300.0
