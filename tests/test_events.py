from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def create_user_and_get_token(client: TestClient, username="eventuser"):
    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@test.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": username, "password": "password123"},
    )
    return response.json()["access_token"]

def test_create_event_success(client, auth_headers):
    payload = {
        "title": "Hackathon 2026",
        "description": "Coding all night",
        "location": "Leeds University",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=5)).isoformat(),
        "capacity": 50
    }

    response = client.post("/events", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hackathon 2026"
    assert data["id"] is not None

def test_list_events_pagination(client: TestClient):
    # Create 15 events
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=3)

    for i in range(15):
        client.post("/events", json={
            "title": f"Event {i}",
            "location": "Test",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "capacity": 10
        }, headers=headers)

    # Test default pagination
    response = client.get("/events?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15

    # Test offset
    response = client.get("/events?limit=10&offset=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5

def test_get_event(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    res = client.post("/events", json={
        "title": "Single Event", "location": "Test", "start_time": start, "end_time": end, "capacity": 10
    }, headers=headers)
    event_id = res.json()["id"]

    # Get
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Event"

def test_update_event(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    res = client.post("/events", json={
        "title": "Old Title", "location": "Test", "start_time": start, "end_time": end, "capacity": 10
    }, headers=headers)
    event_id = res.json()["id"]

    # Update
    response = client.patch(f"/events/{event_id}", json={"title": "New Title"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_delete_event(client: TestClient):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    res = client.post("/events", json={
        "title": "To Delete", "location": "Test", "start_time": start, "end_time": end, "capacity": 10
    }, headers=headers)
    event_id = res.json()["id"]

    # Delete
    response = client.delete(f"/events/{event_id}", headers=headers)
    assert response.status_code == 204

    # Verify deleted
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 404


def test_patch_event_not_found(client: TestClient):
    token = create_user_and_get_token(client, username="patchnf")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/events/99999", json={"title": "Nope"}, headers=headers)
    assert response.status_code == 404


def test_delete_event_not_found(client: TestClient):
    token = create_user_and_get_token(client, username="delnf")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/events/99999", headers=headers)
    assert response.status_code == 404


def test_get_event_not_found(client: TestClient):
    response = client.get("/events/99999")
    assert response.status_code == 404


def test_list_events_with_filters(client: TestClient):
    token = create_user_and_get_token(client, username="filteruser")
    headers = {"Authorization": f"Bearer {token}"}
    start = (datetime.utcnow() + timedelta(days=1)).isoformat()
    end = (datetime.utcnow() + timedelta(days=1, hours=3)).isoformat()

    client.post("/events", json={
        "title": "Filtered Event", "location": "Leeds", "start_time": start, "end_time": end, "capacity": 100
    }, headers=headers)

    resp = client.get("/events?q=Filtered&location=Leeds&min_capacity=50&sort=-start_time")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_list_events_status_filter(client: TestClient):
    token = create_user_and_get_token(client, username="statususer")
    headers = {"Authorization": f"Bearer {token}"}
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    end = (datetime.utcnow() + timedelta(days=30, hours=2)).isoformat()
    client.post("/events", json={
        "title": "Future Event", "location": "X", "start_time": future, "end_time": end, "capacity": 10
    }, headers=headers)

    resp = client.get("/events?status=upcoming")
    assert resp.status_code == 200
