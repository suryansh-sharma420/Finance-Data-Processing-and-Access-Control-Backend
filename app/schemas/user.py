from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    """Common properties for a user."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: bool = True
    role: str = "Viewer"

class UserCreate(UserBase):
    """Requirements for creating a new user."""
    email: EmailStr
    username: str
    password: str

class UserUpdate(UserBase):
    """Fields that can be updated for a user."""
    password: Optional[str] = None

class User(UserBase):
    """Complete user data schema with system IDs."""
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for the access token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for the data contained in the token."""
    user_id: Optional[int] = None
