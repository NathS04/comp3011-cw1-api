
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_security_headers_200():
    r = client.get("/health")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Referrer-Policy"] == "no-referrer"
    assert r.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"
    assert r.headers["Cross-Origin-Resource-Policy"] == "same-site"
    assert r.headers["Cache-Control"] == "no-store"

def test_security_headers_404():
    r = client.get("/nonexistent")
    assert r.status_code == 404
    assert "X-Request-ID" in r.headers
    assert r.headers["X-Frame-Options"] == "DENY"
