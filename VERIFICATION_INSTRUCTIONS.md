# Verification Instructions

**COMP3011 CW1 – Marker Instructions**

---

## 1. Prerequisites

- Python 3.9+
- `jq` (for JSON parsing in curl examples)

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
python -c "import app.main; import requests; print('OK')"
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

```bash
uvicorn app.main:app --port 8000 &
sleep 2
```

---

## 6. Verify /health

```bash
curl -s http://127.0.0.1:8000/health | jq
```

**Expected fields:** `status`, `database` ("ok"), `version`, `environment`, `commit`, `timestamp`

---

## 7. Verify Security Headers

```bash
curl -si http://127.0.0.1:8000/health | head -15
```

**Expected headers:**
- `X-Request-ID: <uuid>`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Cache-Control: no-store`

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

# Try admin endpoint
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/admin/imports | jq
```

**Expected:** `{"detail":"The user doesn't have enough privileges"}`

```bash
# Promote to admin and retry
python scripts/make_admin.py testuser
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/admin/imports | jq
```

**Expected:** `[]` or list of imports

---

## 9. Verify ETag + 304

```bash
# First request
ETAG=$(curl -si http://127.0.0.1:8000/events | grep -i "^etag:" | cut -d' ' -f2 | tr -d '\r')
echo "ETag: $ETAG"

# Conditional request
curl -si -H "If-None-Match: $ETAG" http://127.0.0.1:8000/events | head -10
```

**Expected:** `HTTP/1.1 304 Not Modified` (no body)

---

## 10. Verify Rate Limiting (429)

```bash
export RATE_LIMIT_ENABLED=true

# Flood login endpoint (limit: 10/min)
for i in {1..12}; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8000/auth/login \
    -d "username=fake&password=fake")
  echo "Request $i: $CODE"
done
```

**Expected:** First 10 return 401, then 429

```bash
# Verify 429 includes request_id
curl -s -X POST http://127.0.0.1:8000/auth/login -d "username=fake&password=fake" | jq
```

**Expected:** `{"detail":"Too Many Requests","request_id":"<uuid>"}`

---

## 11. PDF Regeneration Checklist

### Option A: VS Code
1. Install "Markdown PDF" extension
2. Open `.md` file
3. Cmd+Shift+P → "Markdown PDF: Export (pdf)"

### Option B: Pandoc
```bash
pandoc README.md -o README.pdf
pandoc docs/API_DOCUMENTATION.md -o docs/API_DOCUMENTATION.pdf
pandoc TECHNICAL_REPORT.md -o TECHNICAL_REPORT.pdf
pandoc docs/GENAI_EXPORT_LOGS.md -o docs/GENAI_EXPORT_LOGS.pdf
```

### Option C: Browser Print
1. Open `.md` in GitHub or VS Code preview
2. Print → Save as PDF

### PDF Verification
After regeneration, confirm:
- Test count: 39
- Tools: Gemini, Claude, ChatGPT
- /health fields: status, database, version, environment, commit, timestamp

---

## 12. Final QA Checklist

```bash
# Check for stale test counts
grep -r "35 test\|35 passed\|31 test" --include="*.md" .
# Expected: No matches (except this example grep)

# Confirm pytest
pytest -q
# Expected: 39 passed

# Confirm all docs mention 39
grep -r "39" --include="*.md" . | grep -i test
# Should show consistent 39 across files
```

---

*COMP3011 CW1 – Verification Instructions*
