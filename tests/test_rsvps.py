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


def test_rsvp_to_nonexistent_event(client: TestClient):
    headers = get_auth_headers(client, username="rsvpnf")
    resp = client.post("/events/99999/rsvps", json={"attendee_id": 1, "status": "going"}, headers=headers)
    assert resp.status_code == 404
    assert "event" in resp.json()["detail"]


def test_rsvp_with_nonexistent_attendee(client: TestClient):
    headers = get_auth_headers(client, username="rsvpnfatt")
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    e_res = client.post("/events", json={
        "title": "RSVP Att NF", "location": "Test", "start_time": start, "end_time": end, "capacity": 10
    }, headers=headers)
    event_id = e_res.json()["id"]

    resp = client.post(f"/events/{event_id}/rsvps", json={"attendee_id": 99999, "status": "going"}, headers=headers)
    assert resp.status_code == 404
    assert "attendee" in resp.json()["detail"]


def test_delete_rsvp_not_found(client: TestClient):
    headers = get_auth_headers(client, username="rsvpdel")
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    e_res = client.post("/events", json={
        "title": "Del RSVP", "location": "Test", "start_time": start, "end_time": end, "capacity": 10
    }, headers=headers)
    event_id = e_res.json()["id"]

    resp = client.delete(f"/events/{event_id}/rsvps/99999", headers=headers)
    assert resp.status_code == 404


def test_list_rsvps_nonexistent_event(client: TestClient):
    resp = client.get("/events/99999/rsvps")
    assert resp.status_code == 404


def test_event_stats_not_found(client: TestClient):
    resp = client.get("/events/99999/stats")
    assert resp.status_code == 404


def test_non_owner_cannot_rsvp_for_someone_else_attendee(client: TestClient):
    owner_headers = get_auth_headers(client, username="attowner")
    other_headers = get_auth_headers(client, username="attother")
    event_id, attendee_id = setup_event_and_attendee(client, owner_headers)

    resp = client.post(
        f"/events/{event_id}/rsvps",
        json={"attendee_id": attendee_id, "status": "going"},
        headers=other_headers,
    )
    assert resp.status_code == 403
    assert "Not authorised to RSVP" in resp.json()["detail"]


def test_attendee_owner_can_delete_own_rsvp(client: TestClient):
    owner_headers = get_auth_headers(client, username="attownerdel")
    event_id, attendee_id = setup_event_and_attendee(client, owner_headers)
    create = client.post(
        f"/events/{event_id}/rsvps",
        json={"attendee_id": attendee_id, "status": "going"},
        headers=owner_headers,
    )
    rsvp_id = create.json()["id"]

    resp = client.delete(f"/events/{event_id}/rsvps/{rsvp_id}", headers=owner_headers)
    assert resp.status_code == 204


def test_event_owner_can_delete_rsvp_on_their_event(client: TestClient):
    event_owner_headers = get_auth_headers(client, username="eventowner")
    attendee_owner_headers = get_auth_headers(client, username="attendeeowner")
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    e_res = client.post(
        "/events",
        json={"title": "Owner Event", "location": "Test", "start_time": start, "end_time": end, "capacity": 10},
        headers=event_owner_headers,
    )
    event_id = e_res.json()["id"]
    a_res = client.post(
        "/attendees",
        json={"name": "Owned Attendee", "email": "owned-attendee@example.com"},
        headers=attendee_owner_headers,
    )
    attendee_id = a_res.json()["id"]
    create = client.post(
        f"/events/{event_id}/rsvps",
        json={"attendee_id": attendee_id, "status": "going"},
        headers=attendee_owner_headers,
    )
    rsvp_id = create.json()["id"]

    resp = client.delete(f"/events/{event_id}/rsvps/{rsvp_id}", headers=event_owner_headers)
    assert resp.status_code == 204


def test_admin_can_delete_any_rsvp(client: TestClient, db):
    owner_headers = get_auth_headers(client, username="rsvpowner")
    start = datetime.utcnow().isoformat()
    end = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    e_res = client.post(
        "/events",
        json={"title": "Admin Del Event", "location": "Test", "start_time": start, "end_time": end, "capacity": 10},
        headers=owner_headers,
    )
    event_id = e_res.json()["id"]
    a_res = client.post("/attendees", json={"name": "A", "email": "admindel@example.com"}, headers=owner_headers)
    attendee_id = a_res.json()["id"]
    create = client.post(
        f"/events/{event_id}/rsvps",
        json={"attendee_id": attendee_id, "status": "going"},
        headers=owner_headers,
    )
    rsvp_id = create.json()["id"]

    client.post("/auth/register", json={"username": "rsvpadmin", "email": "rsvpadmin@test.com", "password": "password123"})
    from app.models import User
    admin = db.query(User).filter(User.username == "rsvpadmin").first()
    admin.is_admin = True
    db.commit()
    admin_headers = get_auth_headers(client, username="rsvpadmin")

    resp = client.delete(f"/events/{event_id}/rsvps/{rsvp_id}", headers=admin_headers)
    assert resp.status_code == 204


def test_non_owner_non_admin_cannot_delete_other_rsvp(client: TestClient):
    owner_headers = get_auth_headers(client, username="rsvpownera")
    other_headers = get_auth_headers(client, username="rsvpothera")
    event_id, attendee_id = setup_event_and_attendee(client, owner_headers)
    create = client.post(
        f"/events/{event_id}/rsvps",
        json={"attendee_id": attendee_id, "status": "going"},
        headers=owner_headers,
    )
    rsvp_id = create.json()["id"]

    resp = client.delete(f"/events/{event_id}/rsvps/{rsvp_id}", headers=other_headers)
    assert resp.status_code == 403
    assert "Not authorised to delete this RSVP" in resp.json()["detail"]
