
from app.models import DataSource, ImportRun


def _make_admin_headers(client, db, username: str, email: str) -> dict[str, str]:
    client.post("/auth/register", json={"username": username, "email": email, "password": "securepassword"})
    from app.models import User

    user = db.query(User).filter(User.username == username).first()
    user.is_admin = True
    db.commit()
    token = client.post("/auth/login", data={"username": username, "password": "securepassword"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_endpoints_require_auth(client):
    resp = client.post("/admin/imports/run?source_type=csv")
    assert resp.status_code == 401

    resp = client.get("/admin/imports")
    assert resp.status_code == 401

def test_get_dataset_meta(client, db):
    headers = _make_admin_headers(client, db, "adminUser", "admin@example.com")
    resp = client.get("/admin/dataset/meta", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"message": "No dataset imported yet"}

def test_imports_list(client, db):
    headers = _make_admin_headers(client, db, "adminUser2", "admin2@example.com")
    resp = client.get("/admin/imports", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert resp.json() == []


def test_get_dataset_meta_populated(client, db):
    headers = _make_admin_headers(client, db, "adminUser3", "admin3@example.com")
    source = DataSource(name="Leeds Temporary Events", url="http://example.com")
    db.add(source)
    db.commit()
    db.refresh(source)
    run = ImportRun(
        data_source_id=source.id,
        status="success",
        rows_read=5,
        rows_inserted=4,
        rows_updated=1,
        sha256_hash="abc123",
    )
    db.add(run)
    db.commit()

    resp = client.get("/admin/dataset/meta", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_name"] == "Leeds Temporary Events"
    assert data["rows_inserted"] == 4
    assert data["sha256_hash"] == "abc123"


def test_import_quality_empty_state(client, db):
    headers = _make_admin_headers(client, db, "adminUser4", "admin4@example.com")
    resp = client.get("/admin/imports/quality", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_runs"] == 0
    assert data["successful_runs"] == 0
    assert data["failed_runs"] == 0
    assert data["success_rate"] == 0.0
    assert data["runs"] == []
