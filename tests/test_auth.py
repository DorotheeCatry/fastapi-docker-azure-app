from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_session
from app.models.users import User
from app.core.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def client():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("userpass"),
            role="user",
            is_active=True
        )
        session.add(user)
        session.commit()
        
        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

def test_login_success(client):
    """Test successful login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "userpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_register_new_user(client):
    """Test user registration with valid data."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "password" not in data

def test_register_duplicate_username(client):
    """Test user registration with duplicate username."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 400
    assert "Username or email already in use" in response.json()["detail"]

def test_password_validation(client):
    """Test password validation rules."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "weakpass",
            "email": "weak@example.com",
            "password": "weak"
        }
    )
    assert response.status_code == 400
    assert "Password must be at least 8 characters long" in response.json()["detail"]