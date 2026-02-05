import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

def test_admin_import_error_sanitized(client: TestClient, db):
    # Setup Admin User
    user_data = {"username": "adminErr", "email": "err@example.com", "password": "password123"}
    client.post("/auth/register", json=user_data)
    
    from app.models import User
    user = db.query(User).filter(User.username == "adminErr").first()
    user.is_admin = True
    db.commit()
    
    # Login
    token = client.post("/auth/login", data={"username": "adminErr", "password": "password123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mock import_dataset to raise a sensitive error
    with patch("app.api.admin.import_dataset") as mock_import:
        mock_import.side_effect = ValueError("SENSITIVE_DB_PASSWORD_LEAK")
        
        response = client.post("/admin/imports/run?source_type=xml", headers=headers)
        
        # Expect 500
        assert response.status_code == 500
        data = response.json()
        
        # Verify sanitization
        assert data["detail"] == "Internal Server Error"
        assert "request_id" in data
        assert "SENSITIVE" not in response.text
