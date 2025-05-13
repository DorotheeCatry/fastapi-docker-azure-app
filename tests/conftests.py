import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_session
from app.models.users import User
from app.core.security import get_password_hash
import os


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a SQLite in-memory database engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a new database session for testing"""
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    """Create a FastAPI TestClient with the test database session"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session):
    """Create a test user for authentication testing"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("userpass"),
        role="user",
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="test_admin")
def test_admin_fixture(session):
    """Create a test admin user for authentication testing"""
    admin = User(
        username="testadmin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass"),
        role="admin",
        is_active=True
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin