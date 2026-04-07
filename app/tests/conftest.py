import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 1. SET TEST DATABASE ENVIRONMENT BEFORE ANY APP IMPORTS
os.environ["DATABASE_URL"] = "sqlite://"

from app.db import session as db_session
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# 2. CREATE UNIFIED TEST ENGINE WITH STATICPOOL (Memory sharing across threads)
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 3. MONKEY-PATCH THE APP SESSION (Ensures any direct SessionLocal() usage works)
db_session.engine = engine
db_session.SessionLocal.configure(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Provides a fresh database for each test function."""
    # Ensure tables are created on the unified engine
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # SEED MANDATORY ROLES (Categories are now String Enums, but Roles might still be needed)
    from app.db.models.role import Role
    session.add(Role(name="Admin"))
    session.add(Role(name="Viewer"))
    session.commit()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Provides a TestClient with a database session dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
