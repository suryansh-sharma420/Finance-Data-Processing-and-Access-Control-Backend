import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Load database URL from environment or fallback to production SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Creation of a synchronous engine with thread-safe connection pooling for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

# Factory for local session creation on each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for obtaining a database session, ensuring proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
