import pytest
from fastapi.testclient import TestClient

def test_etag_generation(client: TestClient):
    """
    Verify GET requests to /events return an ETag header.
    """
    response = client.get("/events")
    assert response.status_code == 200
    assert "ETag" in response.headers
    assert response.headers["ETag"].startswith('"')
    assert "X-Request-ID" in response.headers

def test_conditional_get_304(client: TestClient):
    """
    Verify If-None-Match results in 304 Not Modified.
    """
    # 1. Initial Fetch
    response = client.get("/events")
    assert response.status_code == 200
    etag = response.headers["ETag"]
    
    # 2. Conditional Fetch
    response2 = client.get("/events", headers={"If-None-Match": etag})
    assert response2.status_code == 304
    # 304 responses must not have a body
    assert not response2.content
    assert response2.headers["ETag"] == etag
    assert "X-Request-ID" in response2.headers

def test_etag_mismatch_200(client: TestClient):
    """
    Verify If-None-Match mismatch results in full 200 response.
    """
    response = client.get("/events", headers={"If-None-Match": '"fake-etag"'})
    assert response.status_code == 200
    assert "ETag" in response.headers
