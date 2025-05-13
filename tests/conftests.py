# Sets up test fixtures that can be reused across all tests
# Creates an in-memory SQLite database for testing
# Provides test users (both regular and admin) for authentication
# Sets up a test client for making API requests

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_session
from app.models.users import User
from app.core.security import get_password_hash


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_db():
    """
    Create an in-memory SQLite database for testing.
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, # 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine

@pytest.fixture(scope="session")
def session(engine):
    """
    Create a new session for the test database.
    """

    with Session(engine) as session:
        yield session

@pytest.fixture(scope="session")
def client(session):
    """
    Create a test client for making API requests.
    """
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def test_user():
    """
    Create a test user for authentication.
    """
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("userpass"),
        role="user",
        is_active=True)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(scope="session")
def test_admin():
    """
    Create a test admin user for authentication.
    """
    admin = User(
        username="testadmin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass"),
        role="admin",
        is_active=True)
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


