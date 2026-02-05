from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from app.core.auth import get_password_hash
from app.api.routes import router

def test_admin_access_forbidden(client: TestClient, db: Session, auth_headers):
    """
    Test that a standard user (from auth_headers fixture) cannot access admin routes.
    """
    response = client.get("/admin/imports", headers=auth_headers)
    assert response.status_code == 403
    assert "privileges" in response.json()["detail"]

def test_admin_access_allowed(client: TestClient, db: Session):
    """
    Test that an admin user can access admin routes.
    """
    # Create admin user
    hashed_pw = get_password_hash("adminpass")
    admin = User(username="superadmin", email="admin@example.com", hashed_password=hashed_pw, is_admin=True)
    db.add(admin)
    db.commit()
    
    # Login
    response = client.post("/auth/login", data={"username": "superadmin", "password": "adminpass"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Access Admin Route
    response = client.get("/admin/dataset/meta", headers=headers)
    assert response.status_code == 200
