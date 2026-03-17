from unittest.mock import patch

from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert data["database"] == "ok"
    assert "version" in data
    assert "commit" in data
    assert "timestamp" in data


def test_health_db_error(client: TestClient):
    """Health endpoint reports database error when DB is unreachable."""
    with patch("app.api.routes.text") as mock_text:
        mock_text.side_effect = Exception("DB down")
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["database"] == "error"
        assert data["status"] == "online"
