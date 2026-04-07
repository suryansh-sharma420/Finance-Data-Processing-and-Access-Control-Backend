from sqlalchemy.ext.declarative import as_declarative
from typing import Any

@as_declarative()
class Base:
    """The source of truth for all database models in the system."""
    id: Any
    __name__: str
