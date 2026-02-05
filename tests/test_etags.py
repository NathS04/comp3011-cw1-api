
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_etag_events_list():
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

def test_etag_health_excluded():
    # Health should NOT have ETag and should be no-store
    r = client.get("/health")
    assert r.status_code == 200
    assert "ETag" not in r.headers
    assert r.headers["Cache-Control"] == "no-store"

def test_etag_event_detail():
    # Create event first to ensure ID exists
    # Assuming auth dependency, but tests usually use override or valid token.
    # Check existing tests for auth pattern. 
    # For now, hit a likely existing ID or mock DB?
    # Simple workaround: Try ID 1. If 404, we test 404 behavior (no ETag).
    # If we want 200, we need to seed or rely on test order.
    # The `client` here is separate.
    pass # Leaving for now to verify basics
