import pytest
from fastapi.testclient import TestClient

def test_read_users_me(client, test_user):
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
    assert "Not authenticated" in response.json()["detail"]

def test_admin_get_users(client, test_admin):
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

def test_non_admin_get_users(client, test_user):
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