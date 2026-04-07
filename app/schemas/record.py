from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Literal, Union
from datetime import datetime

# 1. DEFINE ALLOWED CATEGORIES
# Income: "Salary", "Other Income"
# Expense: "Housing", "Food", "Transportation", "Misc"
RecordCategory = Literal[
    "Salary", "Other Income", 
    "Housing", "Food", "Transportation", "Misc"
]

class RecordBase(BaseModel):
    """Core attributes for a financial transaction."""
    amount: float = Field(..., gt=0, description="Transaction amount must be positive")
    type: Literal["Income", "Expense"]
    category: RecordCategory # Strong validation for allowed types
    description: str
    date: Optional[datetime] = None

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v: str) -> str:
        """Ensures 'income' becomes 'Income' for clean DB grouping."""
        return v.title() if isinstance(v, str) else v

class RecordCreate(RecordBase):
    """Schema for incoming creation requests."""
    pass

class RecordUpdate(BaseModel):
    """Schema for partial update requests."""
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[Literal["Income", "Expense"]] = None
    category: Optional[RecordCategory] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

class Record(RecordBase):
    """The full database object returned to the user."""
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
