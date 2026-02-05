# How to Verify COMP3011 CW1 Submission

**Instructions for Markers / ChatGPT Verification**

To verify this submission is "clean" and runnable from scratch, follow these exact steps in a terminal.

---

## 1. Prerequisite Check
Ensure you have `python3.9+` installed.

---

## 2. Extract & Setup
```bash
# Unzip contents
unzip comp3011-cw1-api_submission.zip -d submission_verify
cd submission_verify

# Create isolated environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (requests included)
pip install -r requirements.txt
```

---

## 3. Verify Boot & Imports
This checks if `requests` and `fastapi` are correctly wired up.
```bash
# This command should run silently and return exit code 0
python -c "import app.main; import requests; print('Imports Verified')"
```

---

## 4. Run Test Suite
```bash
# Database migration (SQLite in-memory or local file)
export DATABASE_URL="sqlite:///./test_verify.db"
export SECRET_KEY="verification_secret"
alembic upgrade head

# Run full test suite
pytest -v
```

**Expected Output:**
- `39 passed`
- `0 failed`
- No `ModuleNotFoundError`

---

## 5. Verify Admin RBAC
```bash
# Start server in background
uvicorn app.main:app --port 8000 &
sleep 2

# Register a user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=testuser&password=password123" | jq -r '.access_token')

# Try admin endpoint (should fail with 403)
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/admin/imports
# Expected: {"detail":"The user doesn't have enough privileges"}

# Promote to admin
python scripts/make_admin.py testuser

# Retry (should succeed)
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/admin/imports
# Expected: [] or list of imports
```

---

## 6. Verify ETag (Conditional GET)
```bash
# First request - get ETag
ETAG=$(curl -si http://127.0.0.1:8000/events | grep -i etag | cut -d' ' -f2 | tr -d '\r')
echo "ETag: $ETAG"

# Second request - use If-None-Match
curl -i -H "If-None-Match: $ETAG" http://127.0.0.1:8000/events
# Expected: HTTP/1.1 304 Not Modified (no body)
```

---

## 7. Verify Rate Limiting (429)
```bash
# Enable rate limiting
export RATE_LIMIT_ENABLED=true

# Flood auth endpoint (11 requests, limit is 10/min)
for i in {1..11}; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/auth/login \
    -d "username=fake&password=fake"
done
# Expected: 10x 401, then 429

# Verify 429 includes request_id
curl -s -X POST http://127.0.0.1:8000/auth/login -d "username=fake&password=fake" | jq
# Expected: {"detail": "Too Many Requests", "request_id": "<uuid>"}
```

---

## 8. Verify Health Endpoint
```bash
curl http://127.0.0.1:8000/health | jq
```

**Expected fields:**
- `status`: "online"
- `database`: "ok"
- `version`: "1.0.0"
- `environment`: "dev" or "prod"
- `commit`: SHA string
- `timestamp`: ISO datetime

---

## 9. Verify Security Headers
```bash
curl -si http://127.0.0.1:8000/health | head -20
```

**Expected headers:**
- `X-Request-ID: <uuid>`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

---

## 10. Start Server (Optional)
```bash
uvicorn app.main:app --port 8000
# Visit http://127.0.0.1:8000/docs
```

---

## PDF Regeneration Checklist

The repository contains PDF versions of documentation. To regenerate after editing:

### Option A: Using a Markdown-to-PDF Tool
```bash
# Install pandoc + wkhtmltopdf
brew install pandoc wkhtmltopdf

# Generate PDFs
pandoc docs/API_DOCUMENTATION.md -o docs/API_DOCUMENTATION.pdf
pandoc TECHNICAL_REPORT.md -o TECHNICAL_REPORT.pdf
pandoc docs/GENAI_EXPORT_LOGS.md -o docs/GENAI_EXPORT_LOGS.pdf
```

### Option B: Using VS Code
1. Install "Markdown PDF" extension
2. Open each `.md` file
3. Cmd+Shift+P → "Markdown PDF: Export (pdf)"

### Option C: Online Converter
1. Upload `.md` file to https://www.markdowntopdf.com/
2. Download PDF
3. Replace existing PDF in repo

### After Regeneration
Verify key numbers match:
- Test count: 39
- Tools used: Gemini, Claude, ChatGPT
- /health fields: status, database, version, environment, commit, timestamp

---

## Final QA Checklist

Before zipping for submission:

```bash
# 1. Verify test count
pytest -q | tail -1
# Expected: 39 passed

# 2. Grep for stale "35" references
grep -r "35 test" --include="*.md" .
# Expected: No matches (all should say 39)

# 3. Grep for consistency
grep -r "Test Count\|tests passing" --include="*.md" .
# All should say 39

# 4. Quick curl checks
curl http://127.0.0.1:8000/health | jq .status          # "online"
curl -si http://127.0.0.1:8000/events | grep X-Request  # Should exist
curl -si http://127.0.0.1:8000/events | grep ETag       # Should exist

# 5. Confirm PDFs match MD content
# Manually open each PDF and verify:
# - Test count: 39
# - ETag section present
# - RBAC section present
```

---

*Verification instructions for COMP3011 CW1 – 5th February 2026*
