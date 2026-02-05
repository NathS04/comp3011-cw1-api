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

**Expected:** `41 passed`

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

**On Render (Production):**
```bash
curl -s https://comp3011-cw1-api.onrender.com/health | jq '.environment'
# Expected: "prod"
```

---

## 7. Verify Security Headers

```bash
curl -si http://127.0.0.1:8000/health | head -20
```

**Expected headers (all responses):**
- `X-Request-ID: <uuid>`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Cross-Origin-Resource-Policy: same-site`
- `Cache-Control: no-store`

**GET /events 200 responses additionally have:**
- `ETag: "<hash>"`
- `Cache-Control: no-cache`

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

# Re-login (admin flag updated)
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=testuser&password=password123" | jq -r '.access_token')

curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/admin/imports
```

**Expected:** `[]` or list of imports

---

## 9. Verify ETag + 304

```bash
# First request - get ETag
RESPONSE=$(curl -si http://127.0.0.1:8000/events)
echo "$RESPONSE" | head -15
ETAG=$(echo "$RESPONSE" | grep -i "^etag:" | cut -d' ' -f2 | tr -d '\r')
echo "ETag: $ETAG"

# Conditional request (same endpoint, no data change)
curl -si -H "If-None-Match: $ETAG" http://127.0.0.1:8000/events
```

**Expected:**
- Status: `HTTP/1.1 304 Not Modified`
- Headers: `ETag` (same value), `X-Request-ID`, `Cache-Control: no-cache`
- Body: **EMPTY** (no content)

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
# Verify 429 response format (after hitting limit)
curl -si -X POST http://127.0.0.1:8000/auth/login -d "username=fake&password=fake"
```

**Expected JSON:** `{"detail":"Too Many Requests","request_id":"<uuid>"}`
**Expected Header:** `X-Request-ID: <uuid>` (matches JSON `request_id`)

---

## 11. Verify Sanitized 500 (Optional)

To verify 500 error sanitization:

```bash
# This requires triggering an internal error safely
# One way: make admin import with broken source (if applicable)
# Otherwise, trust test: tests/test_admin_errors.py validates this
```

**Expected 500 response:** 
```json
{"detail": "Internal Server Error", "request_id": "<uuid>"}
```
- No stack traces
- No exception details
- `request_id` for log correlation

---

## 12. PDF Regeneration

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

### PDF Verification Checklist
After regenerating, verify each PDF contains:
- [ ] Test count: **41 passed**
- [ ] Rate limits: **120/min global, 10/min login**
- [ ] Headers: **X-Request-ID, nosniff, DENY, Referrer-Policy, Permissions-Policy, CORP**
- [ ] /health fields: **status, database, version, environment, commit, timestamp**
- [ ] ETag/304: **described with empty body**

---

## 13. Marker Sanity Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Tests pass | `pytest -q` | `41 passed` |
| Import works | `python3 -c "import app.main"` | No error |
| Health works | `curl /health` | JSON with `database: "ok"` |
| RBAC enforced | `curl -H "Authorization: Bearer $TOKEN" /admin/imports` | 403 for non-admin |
| ETag present | `curl -si /events` | `ETag:` header |
| 304 works | `curl -H "If-None-Match: $ETAG" /events` | 304 status, empty body |
| 429 format | Flood `/auth/login` | `request_id` in JSON |
| Headers present | Any response | `X-Request-ID`, `nosniff`, `DENY`, `Referrer-Policy`, etc. |
| No stale counts | `grep -rn "39 passed" *.md docs/*.md` | No matches |
| No stale counts | `grep -rn "35 passed" *.md docs/*.md` | No matches |

---

*COMP3011 CW1 – Verification Instructions*
