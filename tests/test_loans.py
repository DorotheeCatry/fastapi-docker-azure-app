import pytest
from fastapi.testclient import TestClient

def test_request_loan(client, test_user):
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

def test_get_loan_history(client, test_user, test_loan):
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
    assert response.status_code == 200
    loans = response.json()
    assert isinstance(loans, list)
    assert len(loans) > 0
    assert loans[0]["user_id"] == test_user.id

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
    assert "Not authenticated" in response.json()["detail"]