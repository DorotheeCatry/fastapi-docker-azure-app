from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_session
from app.models.users import User
from app.core.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
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

def test_request_loan(client):
    """Test submitting a loan request."""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "userpass"}
    )
    token = login_response.json()["access_token"]
    
    # Submit loan request
    loan_data = {
        "GrAppv": 50000.0,
        "Term": 60.0,
        "State": "CA",
        "NAICS_Sectors": "44",
        "New": "Yes",
        "Franchise": "0",
        "NoEmp": "10",
        "RevLineCr": "Yes",
        "LowDoc": "No",
        "Rural": "No"
    }
    
    response = client.post(
        "/api/v1/loans/request",
        json=loan_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), bool)

def test_get_loan_history(client):
    """Test retrieving loan history."""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "userpass"}
    )
    token = login_response.json()["access_token"]
    
    # Get loan history
    response = client.get(
        "/api/v1/loans/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]  # 404 is acceptable if no loans exist

def test_loan_request_no_auth(client):
    """Test loan request without authentication."""
    loan_data = {
        "GrAppv": 50000.0,
        "Term": 60.0,
        "State": "CA",
        "NAICS_Sectors": "44",
        "New": "Yes",
        "Franchise": "0",
        "NoEmp": "10",
        "RevLineCr": "Yes",
        "LowDoc": "No",
        "Rural": "No"
    }
    
    response = client.post("/api/v1/loans/request", json=loan_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"