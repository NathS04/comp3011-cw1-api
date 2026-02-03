from datetime import datetime, timedelta
from fastapi.testclient import TestClient

def get_auth_headers(client: TestClient, username="rsvpuser"):
    client.post( "/auth/register", json={"username": username, "email": f"{username}@test.com", "password": "password123"} )
    response = client.post( "/auth/login", data={"username": username, "password": "password123"} )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def setup_event_and_attendee(client: TestClient, headers):
    # Event
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    e_res = client.post("/events", json={
        "title": "RSVP Event", "location": "Test", "start_time": start, "end_time": end, "capacity": 10
    }, headers=headers)
    event_id = e_res.json()["id"]
    
    # Attendee
    a_res = client.post("/attendees", json={"name": "RSVP Person", "email": "rsvp@example.com"}, headers=headers)
    att_id = a_res.json()["id"]
    
    return event_id, att_id

def test_create_rsvp(client: TestClient):
    headers = get_auth_headers(client)
    event_id, att_id = setup_event_and_attendee(client, headers)
    
    response = client.post(
        f"/events/{event_id}/rsvps",
        json={"attendee_id": att_id, "status": "going"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "going"
    assert data["event_id"] == event_id

def test_duplicate_rsvp(client: TestClient):
    headers = get_auth_headers(client)
    event_id, att_id = setup_event_and_attendee(client, headers)
    
    client.post(f"/events/{event_id}/rsvps", json={"attendee_id": att_id, "status": "going"}, headers=headers)
    response = client.post(f"/events/{event_id}/rsvps", json={"attendee_id": att_id, "status": "maybe"}, headers=headers)
    assert response.status_code == 409

def test_list_rsvps(client: TestClient):
    headers = get_auth_headers(client)
    event_id, att_id = setup_event_and_attendee(client, headers)
    client.post(f"/events/{event_id}/rsvps", json={"attendee_id": att_id, "status": "going"}, headers=headers)
    
    response = client.get(f"/events/{event_id}/rsvps", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["attendee_id"] == att_id

def test_event_stats(client: TestClient):
    headers = get_auth_headers(client)
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    # Capacity 5
    e_res = client.post("/events", json={
        "title": "Stats Event", "location": "Test", "start_time": start, "end_time": end, "capacity": 5
    }, headers=headers)
    event_id = e_res.json()["id"]
    
    # Add 2 going, 1 maybe
    for i, status in enumerate(["going", "going", "maybe"]):
        a_res = client.post("/attendees", json={"name": f"P{i}", "email": f"p{i}@example.com"}, headers=headers)
        att_id = a_res.json()["id"]
        client.post(f"/events/{event_id}/rsvps", json={"attendee_id": att_id, "status": status}, headers=headers)
        
    response = client.get(f"/events/{event_id}/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["going"] == 2
    assert data["maybe"] == 1
    assert data["remaining_capacity"] == 3
