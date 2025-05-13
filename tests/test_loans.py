from fastapi.testclient import TestClient
from app.main import app
from app.models.loans import LoanRequests

def test_request_loan_unauthorized(client):
    """
    Test that unauthorized users cannot request loans
    """
    response = client.post(
        "/api/v1/loans/request",
        json={
            "GrAppv": 50000.0,
            "Term": 60,
            "State": "CA",
            "NAICS_Sectors": "44",
            "New": "Yes",
            "Franchise": "No",
            "NoEmp": 5,
            "RevLineCr": "Yes",
            "LowDoc": "No",
            "Rural": "No"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_loan_history_unauthorized(client):
    """
    Test that unauthorized users cannot access loan history
    """
    response = client.get("/api/v1/loans/history")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_request_loan_authorized(client, test_user):
    """
    Test that authorized users can request loans
    """
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "userpass"}
    )
    token = login_response.json()["access_token"]
    
    # Make loan request with token
    response = client.post(
        "/api/v1/loans/request",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "GrAppv": 50000.0,
            "Term": 60,
            "State": "CA",
            "NAICS_Sectors": "44",
            "New": "Yes",
            "Franchise": "No",
            "NoEmp": 5,
            "RevLineCr": "Yes",
            "LowDoc": "No",
            "Rural": "No"
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), bool)  # Should return prediction (True/False)

def test_get_loan_history_authorized(client, test_user):
    """
    Test that authorized users can access their loan history
    """
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "userpass"}
    )
    token = login_response.json()["access_token"]
    
    # Get loan history with token
    response = client.get(
        "/api/v1/loans/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Should return list of loans