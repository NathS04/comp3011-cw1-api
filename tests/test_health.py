from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert data["database"] == "ok"
    assert "version" in data
    assert "commit" in data
