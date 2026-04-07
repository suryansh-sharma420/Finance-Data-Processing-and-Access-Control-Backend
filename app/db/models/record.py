from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Record(Base):
    """
    Represents a financial transaction entry.
    Categorization is implemented as a fixed String Enum for dashboard simplicity.
    """
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False) # Income or Expense
    category = Column(String, nullable=False) # e.g., Salary, Food, Housing
    description = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="records")
