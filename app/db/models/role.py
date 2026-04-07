from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class Role(Base):
    """Defines system roles used across the application."""
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
