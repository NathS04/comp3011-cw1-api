from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core import auth

def test_admin_endpoints_require_auth(client):
    resp = client.post("/admin/imports/run?source_type=csv")
    assert resp.status_code == 401
    
    resp = client.get("/admin/imports")
    assert resp.status_code == 401

def test_get_dataset_meta(client, db):
    # Register/Login as admin (or just user, since logic checks auth)
    # 1. Create User
    user_data = {"username": "adminUser", "email": "admin@example.com", "password": "securepassword"}
    client.post("/auth/register", json=user_data)
    
    # Promote to admin manually
    from app.models import User
    user = db.query(User).filter(User.username == "adminUser").first()
    user.is_admin = True
    db.commit()
    
    # 2. Login
    login_resp = client.post("/auth/login", data={"username": "adminUser", "password": "securepassword"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Get Meta (Empty initially or whatever state DB is in)
    resp = client.get("/admin/dataset/meta", headers=headers)
    assert resp.status_code == 200
    # It might return "No dataset imported yet" or actual meta if data seeded
    
def test_imports_list(client, db):
    # Auth setup
    user_data = {"username": "adminUser2", "email": "admin2@example.com", "password": "securepassword"}
    client.post("/auth/register", json=user_data)
    
    from app.models import User
    user = db.query(User).filter(User.username == "adminUser2").first()
    user.is_admin = True
    db.commit()
    login_resp = client.post("/auth/login", data={"username": "adminUser2", "password": "securepassword"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.get("/admin/imports", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
