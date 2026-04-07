from pydantic import BaseModel
from typing import Optional

class RoleBase(BaseModel):
    """Common role properties."""
    name: Optional[str] = None
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """Requirements to create a role."""
    name: str

class RoleUpdate(RoleBase):
    """Fields to update a role."""
    pass

class Role(RoleBase):
    """Complete role data schema."""
    id: int

    class Config:
        from_attributes = True
