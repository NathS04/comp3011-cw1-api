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

---

## 🚀 Reproducibility

```bash
# Clone & setup
git clone https://github.com/NathS04/comp3011-cw1-api.git && cd comp3011-cw1-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure & run
export DATABASE_URL="sqlite:///./app.db" SECRET_KEY="dev-key-change-me"
alembic upgrade head
pytest -q                    # Expected: 39 passed
uvicorn app.main:app --reload
```

**Verification:** See [VERIFICATION_INSTRUCTIONS.md](VERIFICATION_INSTRUCTIONS.md) for full marker instructions.

---

## ☁️ Deployment (Render)

**Live API:** https://comp3011-cw1-api.onrender.com

> ⚠️ **Note:** Free tier spins down after 15 min inactivity. First request may take ~30–60s (cold start). If you see a 503, try again after 60 seconds.

- `render.yaml` provisions managed PostgreSQL
- Environment: `DATABASE_URL`, `SECRET_KEY`, `ENVIRONMENT=prod`

---

## 📊 Dataset Import

Integrates **Leeds City Council Temporary Event Notices** (XML).

```bash
# Via API (admin JWT required)
curl -X POST "http://127.0.0.1:8000/admin/imports/run?source_type=xml" \
  -H "Authorization: Bearer $TOKEN"
```

**Provenance:** SHA256 hash stored; ImportRun table logs timestamp, duration, row counts.

---

## 🧪 Running Tests

```bash
pytest -v
```

**Result:** 39 tests passing (auth, events, attendees, RSVPs, analytics, admin, RBAC, middleware, ETag, error handling)

---

## 🔌 API Endpoints

### Core CRUD
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check (status, database, version, environment, commit, timestamp) | No |
| POST | `/auth/register` | Register user | No |
| POST | `/auth/login` | Get JWT token | No |
| GET/POST | `/events` | List/Create events | POST: Yes |
| PATCH/DELETE | `/events/{id}` | Update/Delete event | Yes |
| GET | `/events/{id}/stats` | RSVP statistics | No |
| POST | `/attendees` | Create attendee | Yes |
| POST | `/events/{id}/rsvps` | Create RSVP | Yes |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/events/seasonality` | Monthly distribution |
| GET | `/analytics/events/trending` | Trending score |
| GET | `/events/recommendations` | Personalised suggestions (auth required) |

### Admin (Admin-only)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/admin/imports/run` | Trigger dataset import | **Admin** |
| GET | `/admin/imports` | List import runs | **Admin** |
| GET | `/admin/dataset/meta` | Dataset metadata | **Admin** |

> **RBAC:** Non-admin users receive `{"detail":"The user doesn't have enough privileges"}` (403 Forbidden) on `/admin/*` endpoints.

---

## 🔒 Security & Standards

| Feature | Implementation |
|---------|---------------|
| **RBAC** | `is_admin` flag; `/admin/*` returns 403 for non-admin |
| **Rate Limiting** | 120/min global, 10/min login |
| **429 Response** | `{"detail":"Too Many Requests","request_id":"<uuid>"}` |
| **Request Tracing** | `X-Request-ID` header on **all** responses |
| **Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` |
| **Cache-Control** | `no-store` (default) or `no-cache` (GET with ETag) |
| **ETag Caching** | GET responses include ETag; `If-None-Match` → 304 Not Modified |
| **Error Sanitization** | 500 errors: `{"detail":"Internal Server Error","request_id":"<uuid>"}` |
| **CORS** | Configurable via `ALLOWED_ORIGINS` |

---

## 📁 Project Structure

```
comp3011-cw1-api/
├── app/
│   ├── api/            # Routes, analytics, admin
│   ├── core/           # Auth, config, middleware, rate limiting
│   ├── models.py       # SQLAlchemy models (User.is_admin, ImportRun)
│   └── schemas.py      # Pydantic schemas
├── scripts/
│   ├── import_dataset.py   # XML/CSV import with provenance
│   └── make_admin.py       # Promote user to admin
├── tests/              # 39 test cases
├── docs/               # PDF deliverables
└── alembic/            # Migrations
```

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

## 👤 Author

**Nathaniel Sebastian**  
sc232ns@leeds.ac.uk  
University of Leeds, School of Computing

---

*Built with AI assistance – See [docs/GENAI_EXPORT_LOGS.pdf](docs/GENAI_EXPORT_LOGS.pdf) for disclosure*
