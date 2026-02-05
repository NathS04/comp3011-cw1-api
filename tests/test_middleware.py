import pytest
from fastapi.testclient import TestClient
from app.core import rate_limit
from app.core.config import settings

def test_security_headers(client: TestClient):
    """
    Verify security headers are present on responses.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"

def test_rate_limiting_enforced(client: TestClient):
    """
    Verify rate limiter blocks requests when limit exceeded.
    """
    # Enable rate limit temporarily
    original_setting = settings.RATE_LIMIT_ENABLED
    settings.RATE_LIMIT_ENABLED = True
    
    # Reset limiter history
    rate_limit.global_limiter.history.clear()
    
    try:
        # Global limit is 120/min. Let's artificially fill it.
        # It's easier to mock the limiter, but let's try flooding.
        # Actually, let's just mock the 'is_allowed' return for determinism or simple limit check.
        # We'll flood the auth limiter (10/min)
        
        for _ in range(10):
            response = client.post("/auth/login", data={"username": "fake", "password": "fake"})
            # We expect 401 or 429 depending on speed, but first 10 should be processed
            assert response.status_code in [401, 200]
            
        # The 11th request should fail
        response = client.post("/auth/login", data={"username": "fake", "password": "fake"})
        assert response.status_code == 429
        data = response.json()
        assert data["detail"] == "Too Many Requests"
        assert "request_id" in data
        assert "X-Request-ID" in response.headers
        
    finally:
        settings.RATE_LIMIT_ENABLED = original_setting
