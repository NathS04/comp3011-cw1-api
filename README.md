# EventHub – Event & RSVP API

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-39%20passing-brightgreen.svg)](#running-tests)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade REST API for event management with **real-world data integration** from Leeds City Council and **intelligent analytics**. Built for COMP3011 Web Services coursework at the University of Leeds.

---

## 📦 Submission Deliverables

| Document | Format | Path |
|----------|--------|------|
| **API Documentation** | PDF | [docs/API_DOCUMENTATION.pdf](docs/API_DOCUMENTATION.pdf) |
| **Technical Report** | PDF | [TECHNICAL_REPORT.pdf](TECHNICAL_REPORT.pdf) |
| **Presentation Slides** | PPTX | [docs/PRESENTATION_SLIDES.pptx](docs/PRESENTATION_SLIDES.pptx) |
| **GenAI Logs** | PDF | [docs/GENAI_EXPORT_LOGS.pdf](docs/GENAI_EXPORT_LOGS.pdf) |

> All deliverables are included in the repository root and `docs/` folder.

---

## 🚀 Reproducibility

**Fresh Clone Quickstart:**
```bash
# 1. Clone & setup
git clone https://github.com/NathS04/comp3011-cw1-api.git && cd comp3011-cw1-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure & run
export DATABASE_URL="sqlite:///./app.db" SECRET_KEY="dev-key-change-me"
alembic upgrade head
pytest -q                    # Expected: 39 passed
uvicorn app.main:app --reload
```

**Verification:** API documentation at `http://127.0.0.1:8000/docs`  
**Full Instructions:** See [VERIFICATION_INSTRUCTIONS.md](VERIFICATION_INSTRUCTIONS.md)

---

## ☁️ Quickstart (Render Production)

The API is deployed at: **https://comp3011-cw1-api.onrender.com**

**Configuration:**
- `render.yaml` provisions a managed PostgreSQL database
- Environment variables: `DATABASE_URL`, `SECRET_KEY`, `ENVIRONMENT=prod`
- Build command: `pip install -r requirements.txt && alembic upgrade head`

**Known Limitation:** Free tier instances spin down after 15 minutes of inactivity. First request may take ~30 seconds.

---

## 📊 Dataset Import

The system integrates real event data from **Leeds City Council Temporary Event Notices**.

### Option 1: Remote XML (Recommended)
```bash
# Fetch and import latest data directly from Leeds Open Data
python scripts/import_dataset.py --type xml

# Or trigger via API (requires admin JWT)
curl -X POST "http://127.0.0.1:8000/admin/imports/run?source_type=xml" \
  -H "Authorization: Bearer $TOKEN"
```

### Option 2: Local CSV
```bash
python scripts/import_dataset.py --type csv --url data/sample/dataset_sample.csv
```

**Provenance Features:**
- SHA256 hash of source data stored for integrity verification
- Import runs logged with timestamp, duration, and row counts
- Idempotent: re-running updates existing records, doesn't duplicate

---

## 🧪 Demo Script

```bash
# Health check (includes metadata)
curl http://127.0.0.1:8000/health
# → {"status": "online", "database": "ok", "version": "1.0.0", "environment": "dev", "commit": "...", "timestamp": "..."}

# Register user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.com","password":"password123"}'

# Login and capture token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=demo&password=password123" | jq -r '.access_token')

# Create event
curl -X POST http://127.0.0.1:8000/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo Event","location":"Leeds","start_time":"2026-03-01T10:00:00","end_time":"2026-03-01T12:00:00","capacity":50}'

# Analytics
curl http://127.0.0.1:8000/analytics/events/seasonality
curl http://127.0.0.1:8000/analytics/events/trending
```

---

## 🧪 Running Tests

```bash
pytest -v
```

**Result:** 39 tests passing (auth, events, attendees, RSVPs, analytics, admin, provenance, RBAC, middleware, ETag)

---

## 🔌 API Endpoints

### Core CRUD
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check with metadata | No |
| POST | `/auth/register` | Register user | No |
| POST | `/auth/login` | Get JWT token | No |
| GET/POST | `/events` | List/Create events | POST: Yes |
| PATCH/DELETE | `/events/{id}` | Update/Delete event | Yes |
| GET | `/events/{id}/stats` | RSVP statistics | No |
| POST | `/attendees` | Create attendee | Yes |
| POST | `/events/{id}/rsvps` | Create RSVP | Yes |

### Analytics (Novel Features)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/events/seasonality` | Monthly distribution with top locations |
| GET | `/analytics/events/trending` | Trending score based on recent RSVPs |
| GET | `/events/recommendations` | Personalised suggestions (auth required) |

### Admin (Dataset Management)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/admin/imports/run` | Trigger dataset import | Admin |
| GET | `/admin/imports` | List recent import runs | Admin |
| GET | `/admin/dataset/meta` | Current dataset metadata | Admin |

> **Note:** Admin endpoints return `403 Forbidden` for non-admin users.

---

## 📁 Project Structure

```
comp3011-cw1-api/
├── app/
│   ├── api/
│   │   ├── routes.py        # Core CRUD endpoints
│   │   ├── analytics.py     # Analytics & recommendations
│   │   └── admin.py         # Dataset import management
│   ├── core/                # Auth, config, middleware
│   ├── models.py            # SQLAlchemy models
│   └── schemas.py           # Pydantic schemas
├── scripts/
│   ├── import_dataset.py    # XML/CSV import with provenance
│   ├── make_admin.py        # Promote user to admin
│   └── smoke_test.sh        # Deployment verification
├── tests/                   # 39 test cases
├── docs/                    # PDF/PPTX deliverables
└── alembic/                 # Database migrations
```

---

## 🔒 Security Hardening

| Feature | Implementation |
|---------|---------------|
| **RBAC** | `is_admin` flag on User model; `/admin/*` routes require admin (403 otherwise) |
| **Rate Limiting** | In-memory: 120 req/min global, 10 req/min on `/auth/login`; 429 includes `request_id` |
| **Request Tracing** | `X-Request-ID` header on **every** response (including 429/500); included in error JSON |
| **Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Cache-Control: no-store` |
| **ETag Caching** | GET responses include ETag; `If-None-Match` returns `304 Not Modified` |
| **CORS** | Configurable via `ALLOWED_ORIGINS` env; defaults to permissive in dev, strict in prod |
| **Error Sanitization** | 500 errors show generic message + request_id; no stack traces leaked |

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL (prod) / SQLite (dev) |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Auth | JWT (python-jose) |
| Testing | pytest |
| Deployment | Render.com |

---

## ✅ Verification

For markers: see [VERIFICATION_INSTRUCTIONS.md](VERIFICATION_INSTRUCTIONS.md) for step-by-step verification including:
- Clean install test
- Test suite (`pytest -q` → 39 passed)
- Admin RBAC verification (403 → promote → success)
- ETag/304 verification
- Rate limiting check (429)

---

## 👤 Author

**Nathaniel Sebastian**  
sc232ns@leeds.ac.uk  
University of Leeds, School of Computing

---

*Built with AI assistance for COMP3011 CW1 – See [docs/GENAI_EXPORT_LOGS.pdf](docs/GENAI_EXPORT_LOGS.pdf) for full disclosure*
