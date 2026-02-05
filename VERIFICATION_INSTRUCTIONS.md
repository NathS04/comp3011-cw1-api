# Verification Instructions

**COMP3011 CW1 – Marker Instructions**

---

## 1. Prerequisites

- Python 3.9+
- `jq` (optional, for JSON parsing)

---

## 2. Extract & Setup

```bash
unzip comp3011-cw1-api_submission.zip -d verify && cd verify/comp3011-cw1-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Verify Imports

```bash
python3 -c "import app.main; import requests; print('OK')"
# Expected: OK
```

---

## 4. Run Tests

```bash
export DATABASE_URL="sqlite:///./test.db" SECRET_KEY="test"
alembic upgrade head
pytest -q
```

**Expected:** `39 passed`

---

## 5. Start Server

> ⚠️ **Important:** Set environment variables BEFORE starting the server.

```bash
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test"
export RATE_LIMIT_ENABLED="true"
uvicorn app.main:app --port 8000 &
sleep 2
```

---

## 6. Verify /health

```bash
curl -s http://127.0.0.1:8000/health | jq
```

**Expected fields:** `status` ("online"), `database` ("ok"), `version`, `environment`, `commit`, `timestamp`

---

## 7. Verify Security Headers

```bash
curl -si http://127.0.0.1:8000/health | head -15
```

**Expected headers on non-GET or non-200 responses:**
- `X-Request-ID: <uuid>`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Cache-Control: no-store`

**Expected headers on GET 200 responses (with ETag):**
- `X-Request-ID: <uuid>`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Cache-Control: no-cache`
- `ETag: "<hash>"`

---

## 8. Verify RBAC (403)

```bash
# Register non-admin user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=testuser&password=password123" | jq -r '.access_token')

# Try admin endpoint (should fail)
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/admin/imports
```

**Expected:** `{"detail":"The user doesn't have enough privileges"}`

```bash
# Promote to admin and retry
python3 scripts/make_admin.py testuser
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/admin/imports
```

**Expected:** `[]` or list of imports

---

## 9. Verify ETag + 304

Use `/health` for a stable endpoint (body changes with timestamp, so use `/events` for best results):

```bash
# Create an event first for stable content
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"etag_test","email":"etag@example.com","password":"password123"}' 2>/dev/null

# First request - get ETag
RESPONSE=$(curl -si http://127.0.0.1:8000/events)
echo "$RESPONSE" | head -15
ETAG=$(echo "$RESPONSE" | grep -i "^etag:" | cut -d' ' -f2 | tr -d '\r')
echo "ETag: $ETAG"

# Conditional request (same endpoint, no data change)
curl -si -H "If-None-Match: $ETAG" http://127.0.0.1:8000/events | head -10
```

**Expected:** `HTTP/1.1 304 Not Modified` with:
- `ETag` header (same value)
- `X-Request-ID` header
- `Cache-Control: no-cache`
- No body

---

## 10. Verify Rate Limiting (429)

```bash
# Flood login endpoint (limit: 10/min)
for i in {1..12}; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8000/auth/login \
    -d "username=fake&password=fake")
  echo "Request $i: $CODE"
done
```

**Expected:** First 10 return 401, then 429

```bash
# Verify 429 response format
curl -s -X POST http://127.0.0.1:8000/auth/login -d "username=fake&password=fake"
```

**Expected:** `{"detail":"Too Many Requests","request_id":"<uuid>"}`

---

## 11. PDF Regeneration

### Option A: VS Code
1. Install "Markdown PDF" extension
2. Open each `.md` file
3. Cmd+Shift+P → "Markdown PDF: Export (pdf)"

### Option B: Pandoc
```bash
pandoc docs/API_DOCUMENTATION.md -o docs/API_DOCUMENTATION.pdf
pandoc TECHNICAL_REPORT.md -o TECHNICAL_REPORT.pdf
pandoc docs/GENAI_EXPORT_LOGS.md -o docs/GENAI_EXPORT_LOGS.pdf
```

---

## 12. Marker Sanity Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Tests pass | `pytest -q` | `39 passed` |
| Import works | `python3 -c "import app.main"` | No error |
| Health works | `curl /health` | JSON with `database: "ok"` |
| RBAC enforced | `curl -H "Auth: Bearer $TOKEN" /admin/imports` | 403 for non-admin |
| ETag present | `curl -si /events` | `ETag:` header |
| 304 works | `curl -H "If-None-Match: $ETAG" /events` | 304 status |
| 429 format | Flood `/auth/login` | `request_id` in JSON |
| Headers present | Any response | `X-Request-ID`, `nosniff`, `DENY` |
| No stale counts | `grep -r "35 passed" *.md` | No matches |

---

*COMP3011 CW1 – Verification Instructions*
