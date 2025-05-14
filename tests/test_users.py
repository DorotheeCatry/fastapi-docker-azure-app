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
        # Create test admin
        admin = User(
            username="testadmin",
            email="admin@example.com",
            hashed_password=get_password_hash("adminpass"),
            role="admin",
            is_active=True
        )
        session.add(user)
        session.add(admin)
        session.commit()
        
        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

def test_read_users_me(client):
    """Test getting current user details."""
    # First login to get the token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "userpass"}
    )
    token = login_response.json()["access_token"]
    
    # Use the token to get user details
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_read_users_me_no_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_admin_get_users(client):
    """Test admin accessing users list."""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "adminpass"}
    )
    token = login_response.json()["access_token"]
    
    # Get users list
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Users" in response.json()

def test_non_admin_get_users(client):
    """Test non-admin trying to access users list."""
    # Login as regular user
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "userpass"}
    )
    token = login_response.json()["access_token"]
    
    # Try to get users list
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Admins only" in response.json()["detail"]