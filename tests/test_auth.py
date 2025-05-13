from fastapi.testclient import TestClient
from app.main import app

def test_login_success(client, test_user):
    """
    Test successful login with valid credentials.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "userpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """
    Test login with wrong password.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_register_new_user(client):
    """
    Test user registration with valid data.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"

def test_register_duplicate_username(client, test_user):
    """
    Test user registration with duplicate username.
    """
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