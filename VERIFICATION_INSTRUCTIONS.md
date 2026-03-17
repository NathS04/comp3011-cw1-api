# Verification Instructions

**COMP3011 CW1 – Marker Instructions**
**Last Updated:** 17th March 2026

---

## 1. Prerequisites

- Python 3.11+
- `jq` (optional, for JSON parsing)

---

## 2. Extract & Setup

```bash
unzip comp3011-cw1-api_submission_FINAL.zip -d verify && cd verify/comp3011-cw1-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## 3. Run Tests

```bash
pytest -q
```

**Expected:** `84 passed` in under 2 seconds.

---

## 4. Quality Gates

```bash
ruff check .                                          # Expected: All checks passed!
mypy app scripts/import_dataset.py scripts/make_admin.py scripts/clean_db.py  # Expected: Success
bandit -r app scripts -q                              # Expected: No medium/high issues
pytest --cov=app --cov-report=term-missing -q         # Expected: 95% app coverage
```

---

## 5. Start the API

```bash
export DATABASE_URL="sqlite:///./app.db" SECRET_KEY="test-secret-key"
alembic upgrade head
uvicorn app.main:app --port 8000
```

---

## 6. Verify Health

```bash
curl -s http://localhost:8000/health | jq .
```

Expected: `{"status": "online", "database": "ok", "version": "1.0.0", ...}`

---

## 7. Verify Authentication

```bash
# Register
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"marker","email":"marker@test.com","password":"SecurePass123"}' | jq .

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=marker&password=SecurePass123" | jq -r '.access_token')
echo "Token: $TOKEN"
```

---

## 8. Verify Event CRUD with Ownership

```bash
# Create event (stores created_by_user_id)
curl -s -X POST http://localhost:8000/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Event","location":"Leeds","start_time":"2026-12-01T10:00:00Z","end_time":"2026-12-01T12:00:00Z","capacity":50}' | jq .

# Owner can patch
curl -s -X PATCH http://localhost:8000/events/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Event"}' | jq .
# Expected: 200 with updated title

# Register second user
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"other","email":"other@test.com","password":"OtherPass123"}' > /dev/null
TOKEN2=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=other&password=OtherPass123" | jq -r '.access_token')

# Non-owner gets 403
curl -s -X PATCH http://localhost:8000/events/1 \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hijack"}' | jq .
# Expected: 403 "Not authorised to modify this event"
```

---

## 9. Verify Attendee / RSVP Ownership

```bash
# Owner creates attendee
curl -s -X POST http://localhost:8000/attendees \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Marker Attendee","email":"marker-attendee@test.com"}' | jq .

# Owner can RSVP that attendee to the event
curl -s -X POST http://localhost:8000/events/1/rsvps \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"attendee_id":1,"status":"going"}' | jq .

# Different non-admin user cannot RSVP someone else's attendee
curl -s -X POST http://localhost:8000/events/1/rsvps \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"attendee_id":1,"status":"going"}' | jq .
# Expected: 403 "Not authorised to RSVP for this attendee"
```

---

## 10. Verify Provenance (Novel Feature)

```bash
# For user-created event
curl -s http://localhost:8000/events/1/provenance | jq .
# Expected: {"event_id": 1, "is_user_created": true, "source_name": null, ...}

# Import external data (admin required)
python3 scripts/make_admin.py marker
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=marker&password=SecurePass123" | jq -r '.access_token')

curl -s -X POST "http://localhost:8000/admin/imports/run?source_type=csv&source_url=scripts/sample_events_dataset.csv" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Check provenance for imported event
curl -s http://localhost:8000/events/2/provenance | jq .
# Expected: is_user_created=false, source_name, sha256_hash populated
```

---

## 11. Verify ETag & 304

```bash
ETAG=$(curl -si http://localhost:8000/events | grep -i "^etag:" | cut -d' ' -f2 | tr -d '\r')
echo "ETag: $ETAG"

curl -si -H "If-None-Match: $ETAG" http://localhost:8000/events
# Expected: HTTP/1.1 304 Not Modified, empty body
```

---

## 12. Verify Security Headers

```bash
curl -si http://localhost:8000/health | head -15
```

Expected headers: `X-Request-ID`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Permissions-Policy`, `Cross-Origin-Resource-Policy: same-site`.

---

## 13. Verify RBAC

```bash
# Non-admin cannot access /admin/*
curl -s -H "Authorization: Bearer $TOKEN2" http://localhost:8000/admin/imports | jq .
# Expected: 403 "The user doesn't have enough privileges"

# Admin can access
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/imports | jq .
# Expected: 200 with list of imports

# Import quality analytics
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/imports/quality | jq .
# Expected: 200 with {total_runs, successful, failed, runs: [...]}
```

---

## 14. Verify Analytics

```bash
curl -s http://localhost:8000/analytics/events/seasonality | jq .
# Expected: {items: [{month, count, top_locations}]}

curl -s http://localhost:8000/analytics/events/trending | jq .
# Expected: list of trending events with scores
```

---

## 15. Submission Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Tests pass | `pytest -q` | 84 passed |
| Ruff clean | `ruff check .` | All checks passed |
| Mypy clean | `mypy app scripts/import_dataset.py scripts/make_admin.py scripts/clean_db.py` | Success |
| Bandit clean | `bandit -r app scripts -q` | No medium/high |
| Coverage target | `pytest --cov=app --cov-report=term-missing -q` | 95% app coverage |
| Technical report exists | `ls TECHNICAL_REPORT.pdf` | File present |
| API docs exist | `ls docs/API_DOCUMENTATION.pdf` | File present |
| GenAI logs exist | `ls docs/GENAI_EXPORT_LOGS.pdf` | File present |
| Health endpoint | `curl localhost:8000/health` | status: online |
| Ownership enforced | See sections 8-9 | 403 for non-owner |
| Provenance works | See section 10 | Lineage returned |
| ETag works | See section 11 | 304 returned |

---

*COMP3011 CW1 – Verification Instructions*
