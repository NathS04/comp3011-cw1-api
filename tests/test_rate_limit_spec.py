
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_rate_limit_login():
    # Hit login 10 times (allowed)
    for _ in range(10):
        r = client.post("/auth/login", data={"username": "test", "password": "pw"})
        # We expect 200 or 401, mostly 401 if user invalid
        assert r.status_code in [200, 401]

    # 11th time -> 429
    r = client.post("/auth/login", data={"username": "test", "password": "pw"})
    assert r.status_code == 429
    
    data = r.json()
    assert data["detail"] == "Too Many Requests"
    assert "request_id" in data
    
    # Check headers
    assert "X-Request-ID" in r.headers
    assert r.headers["X-Request-ID"] == data["request_id"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
