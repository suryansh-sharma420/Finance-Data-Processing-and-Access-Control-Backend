from fastapi import status
from sqlalchemy.orm import Session
from app.core import security
from app.db.models.user import User

def test_create_user_as_admin(db: Session, client):
    """Verifies that an Admin can successfully register a new user via the API."""
    # 1. Create a mock admin user for authorization
    admin_password = "adminpassword123"
    hashed_pwd = security.get_password_hash(admin_password)
    admin_user = User(email="super@zorvyn.com", username="superadmin", hashed_password=hashed_pwd, is_superuser=True)
    db.add(admin_user)
    db.commit()
    
    # 2. Get admin token
    token = security.create_access_token(subject=admin_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create a target user via API
    email = "newuser@example.com"
    password = "password123"
    username = "newuser"
    
    response = client.post(
        "/api/v1/users/",
        json={"email": email, "password": password, "username": username},
        headers=headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == email
    assert data["username"] == username
    assert "id" in data

def test_login_success(db: Session, client):
    """Verifies that an existing user can authenticate and receive a token."""
    # First create a user manually in DB
    email = "login@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password, username="loginuser", is_active=True)
    db.add(user)
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_read_user_me(db: Session, client):
    """Verifies that the /me endpoint returns the correct profile for an authorized user."""
    # Create user and get token
    email = "me@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password, username="meuser", is_active=True)
    db.add(user)
    db.commit()
    
    token = security.create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == email
    assert data["id"] == user.id
