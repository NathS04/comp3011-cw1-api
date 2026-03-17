"""Tests for event ownership and authorization enforcement."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.models import User


def _make_user(client: TestClient, db, username: str, is_admin: bool = False) -> dict[str, str]:
    """Register a user, optionally promote to admin, and return auth headers."""
    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@test.com", "password": "password123"},
    )
    if is_admin:
        user = db.query(User).filter(User.username == username).first()
        user.is_admin = True
        db.commit()
    resp = client.post("/auth/login", data={"username": username, "password": "password123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_event(client: TestClient, headers: dict[str, str]) -> int:
    payload = {
        "title": "Owned Event",
        "location": "Test",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=2)).isoformat(),
        "capacity": 50,
    }
    resp = client.post("/events", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_owner_can_patch_own_event(client: TestClient, db):
    headers = _make_user(client, db, "owner1")
    event_id = _create_event(client, headers)

    resp = client.patch(f"/events/{event_id}", json={"title": "Updated"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_non_owner_gets_403_on_patch(client: TestClient, db):
    owner_h = _make_user(client, db, "owner2")
    other_h = _make_user(client, db, "other2")
    event_id = _create_event(client, owner_h)

    resp = client.patch(f"/events/{event_id}", json={"title": "Hijack"}, headers=other_h)
    assert resp.status_code == 403
    assert "authorised" in resp.json()["detail"].lower()


def test_admin_can_patch_any_event(client: TestClient, db):
    owner_h = _make_user(client, db, "owner3")
    admin_h = _make_user(client, db, "admin3", is_admin=True)
    event_id = _create_event(client, owner_h)

    resp = client.patch(f"/events/{event_id}", json={"title": "Admin Fix"}, headers=admin_h)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Admin Fix"


def test_non_owner_cannot_delete(client: TestClient, db):
    owner_h = _make_user(client, db, "owner4")
    other_h = _make_user(client, db, "other4")
    event_id = _create_event(client, owner_h)

    resp = client.delete(f"/events/{event_id}", headers=other_h)
    assert resp.status_code == 403


def test_admin_can_delete_any_event(client: TestClient, db):
    owner_h = _make_user(client, db, "owner5")
    admin_h = _make_user(client, db, "admin5", is_admin=True)
    event_id = _create_event(client, owner_h)

    resp = client.delete(f"/events/{event_id}", headers=admin_h)
    assert resp.status_code == 204


def test_public_read_still_works(client: TestClient, db):
    """Public endpoints remain accessible without auth."""
    owner_h = _make_user(client, db, "owner6")
    event_id = _create_event(client, owner_h)

    resp = client.get(f"/events/{event_id}")
    assert resp.status_code == 200

    resp = client.get("/events")
    assert resp.status_code == 200


def test_owner_can_delete_own_event(client: TestClient, db):
    headers = _make_user(client, db, "owner7")
    event_id = _create_event(client, headers)

    resp = client.delete(f"/events/{event_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"/events/{event_id}")
    assert resp.status_code == 404
