from fastapi.testclient import TestClient

def create_user_and_get_token(client: TestClient, username="attendeeuser"):
    client.post( "/auth/register", json={"username": username, "email": f"{username}@test.com", "password": "password123"} )
    response = client.post( "/auth/login", data={"username": username, "password": "password123"} )
    return response.json()["access_token"]

def test_create_attendee(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/attendees",
        json={"name": "John Doe", "email": "john@example.com"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"

def test_create_duplicate_attendee(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    client.post("/attendees", json={"name": "John Doe", "email": "unique@example.com"}, headers=headers)
    response = client.post("/attendees", json={"name": "Jane Doe", "email": "unique@example.com"}, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "email already exists"

def test_get_attendee(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.post("/attendees", json={"name": "Get Me", "email": "getme@example.com"}, headers=headers)
    att_id = res.json()["id"]
    
    response = client.get(f"/attendees/{att_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Me"

def test_get_attendee_not_found(client: TestClient):
    response = client.get("/attendees/99999")
    assert response.status_code == 404
