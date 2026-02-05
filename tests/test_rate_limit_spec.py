from fastapi.testclient import TestClient
from app.main import app
from app.core.rate_limit import auth_limiter

client = TestClient(app, base_url="http://127.0.0.1")

def test_rate_limit_login():
    # Manually reset history to avoid contamination
    auth_limiter.history.clear()
    
    # Hit login 10 times (allowed)
    for i in range(10):
        r = client.post("/auth/login", data={"username": "test", "password": "pw"})
        assert r.status_code in [200, 401], f"Request {i+1} failed with {r.status_code}"

    # 11th time -> 429
    r = client.post("/auth/login", data={"username": "test", "password": "pw"})
    # DEBUG info if fail
    if r.status_code != 429:
        print(f"\nRequests made: {len(auth_limiter.history['127.0.0.1:/auth/login'])}")
        print(f"History: {auth_limiter.history}")
        
    assert r.status_code == 429, f"Expected 429, got {r.status_code}"
    
    data = r.json()
    assert data["detail"] == "Too Many Requests"
    assert "request_id" in data
    
    # Check headers
    assert "X-Request-ID" in r.headers
    assert r.headers["X-Request-ID"] == data["request_id"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
