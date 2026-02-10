
from fastapi.testclient import TestClient
from app.main import app


def test_etag_events_list(client):
    # 1. Initial Request -> 200 + ETag + cache headers
    r = client.get("/events")
    assert r.status_code == 200
    assert "ETag" in r.headers
    assert r.headers["Cache-Control"] == "no-cache"
    
    etag = r.headers["ETag"]
    
    # 2. Conditional Request -> 304 + Empty Body
    r2 = client.get("/events", headers={"If-None-Match": etag})
    assert r2.status_code == 304
    assert not r2.content  # Empty body
    assert r2.headers["ETag"] == etag
    assert r2.headers["Cache-Control"] == "no-cache"
    assert "X-Request-ID" in r2.headers  # Middleware still runs

def test_etag_health_excluded(client):
    # Health should NOT have ETag and should be no-store
    r = client.get("/health")
    assert r.status_code == 200
    assert "ETag" not in r.headers
    assert r.headers["Cache-Control"] == "no-store"

def test_etag_event_detail(client, auth_headers):
    # 1. Create a test event
    payload = {
        "title": "ETag Test Event",
        "location": "Virtual",
        "start_time": "2026-01-01T10:00:00",
        "end_time": "2026-01-01T12:00:00",
        "capacity": 100
    }
    create_res = client.post("/events", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    event_id = create_res.json()["id"]

    # 2. Get Event -> 200 + ETag
    r = client.get(f"/events/{event_id}")
    assert r.status_code == 200
    assert "ETag" in r.headers
    etag = r.headers["ETag"]

    # 3. Conditional Get -> 304
    r2 = client.get(f"/events/{event_id}", headers={"If-None-Match": etag})
    assert r2.status_code == 304
    assert not r2.content
    assert r2.headers["ETag"] == etag
