from fastapi.testclient import TestClient
from app.main import app

def test_read_users_me_unauthorized(client):
    """
    Test that unauthorized users cannot access their profile
    """
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_read_users_me_authorized(client, test_user):
    """
    Test that authorized users can access their profile
    """
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "userpass"}
    )
    token = login_response.json()["access_token"]
    
    # Get profile with token
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"

def test_create_user_unauthorized(client):
    """
    Test that unauthorized users cannot create new users
    """
    response = client.post(
        "/api/v1/admin/users",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass",
            "role": "user"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_create_user_authorized(client, test_admin):
    """
    Test that admin users can create new users
    """
    # First login as admin to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "adminpass"}
    )
    token = login_response.json()["access_token"]
    
    # Create new user with admin token
    response = client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass",
            "role": "user"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"

def test_get_users_unauthorized(client):
    """
    Test that unauthorized users cannot list all users
    """
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_users_authorized(client, test_admin):
    """
    Test that admin users can list all users
    """
    # First login as admin to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "adminpass"}
    )
    token = login_response.json()["access_token"]
    
    # Get users list with admin token
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json()["Users"], list)
    assert "testadmin" in response.json()["Users"]