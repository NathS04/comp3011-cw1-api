from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_username(client: TestClient):
    client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "other@example.com", "password": "password123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_user(client: TestClient):
    # Register first
    client.post(
        "/auth/register",
        json={"username": "testlogin", "email": "login@example.com", "password": "password123"},
    )
    # Login
    response = client.post(
        "/auth/login",
        data={"username": "testlogin", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient):
    client.post(
        "/auth/register",
        json={"username": "wrongpw", "email": "wrong@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "wrongpw", "password": "wrongpassword"},
    )
    assert response.status_code == 401

def test_login_non_existent_user(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_protected_route_without_token(client: TestClient):
    response = client.post(
        "/events",
        json={"title": "Test", "location": "Test", "start_time": "2026-01-01T10:00:00", "end_time": "2026-01-01T11:00:00", "capacity": 10},
    )
    assert response.status_code == 401
