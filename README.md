# EventHub – Event & RSVP API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com)
[![CI](https://github.com/NathS04/comp3011-cw1-api/actions/workflows/ci.yml/badge.svg)](https://github.com/NathS04/comp3011-cw1-api/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-84%20passing-brightgreen.svg)](#running-tests)
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)](#running-tests)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready FastAPI REST API for event management, featuring **real-world data integration** from Leeds City Council, **secure role-based access control**, **data provenance tracking**, and **intelligent analytics**. Built for the COMP3011 Web Services coursework at the University of Leeds.

---

## Submission Deliverables

| Document | Format | Path |
|----------|--------|------|
| **Live API** | URL | [comp3011-cw1-api.onrender.com](https://comp3011-cw1-api.onrender.com) |
| **API Documentation** | PDF | [docs/API_DOCUMENTATION.pdf](docs/API_DOCUMENTATION.pdf) |
| **Technical Report** | PDF | [TECHNICAL_REPORT.pdf](TECHNICAL_REPORT.pdf) |
| **Presentation Slides** | PPTX | [docs/PRESENTATION_SLIDES.pptx](docs/PRESENTATION_SLIDES.pptx) |
| **GenAI Logs** | PDF | [docs/GENAI_EXPORT_LOGS.pdf](docs/GENAI_EXPORT_LOGS.pdf) |

---

## Quickstart

```bash
git clone https://github.com/NathS04/comp3011-cw1-api.git && cd comp3011-cw1-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL="sqlite:///./app.db" SECRET_KEY="dev-key-change-me"
alembic upgrade head
pytest -q                    # Expected: 84 passed
uvicorn app.main:app --reload
```

**Verification:** See [VERIFICATION_INSTRUCTIONS.md](VERIFICATION_INSTRUCTIONS.md) for full marker instructions.

---

## Deployment (Render)

**Live API:** https://comp3011-cw1-api.onrender.com

> **Note:** Free tier spins down after 15 min inactivity. First request may take 30-60s (cold start).

- `render.yaml` provisions managed PostgreSQL
- Environment: `DATABASE_URL`, `SECRET_KEY`, `ENVIRONMENT=prod`

---

## Security

| Feature | Implementation |
|---------|---------------|
| **Authentication** | JWT Bearer (HS256, 30-min expiry) |
| **Password Hashing** | PBKDF2-SHA256 |
| **RBAC** | Anonymous (read), Authenticated (CRUD), Admin (imports) |
| **Event Ownership** | `created_by_user_id`; only owner or admin can PATCH/DELETE |
| **Attendee / RSVP Ownership** | Attendees store `owner_user_id`; RSVP create/delete is restricted to attendee owner, event owner, or admin as appropriate |
| **Rate Limiting** | 120/min global, 10/min login |
| **Security Headers** | X-Request-ID, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, CORP |
| **ETag Caching** | SHA256 body hash; `If-None-Match` returns 304 (RFC 7232) |
| **Error Sanitisation** | Generic 500 with `request_id`; no stack traces |
| **XML Safety** | `defusedxml` prevents XXE attacks |

---

## Key Features

- **24 REST endpoints** covering events, attendees, RSVPs, analytics, auth, admin
- **Event provenance** — `GET /events/{id}/provenance` returns full data lineage
- **Import quality analytics** — `GET /admin/imports/quality` for import health monitoring
- **Dialect-aware analytics** — SQLite and PostgreSQL both supported
- **External dataset integration** — Leeds City Council event notices (XML/CSV)

---

## Running Tests

```bash
pytest -q                    # 84 tests, <2s runtime
pytest --cov=app             # 95% coverage
```

**Quality gates:**

```bash
ruff check .                                                           # Linting (clean)
mypy app scripts/import_dataset.py scripts/make_admin.py scripts/clean_db.py
bandit -r app scripts -q                                               # Security scanning (clean)
./scripts/quality_check.sh                                             # Full marker-style pipeline
```

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | - | System health |
| POST | /auth/register | - | Register user |
| POST | /auth/login | - | Get JWT token |
| GET | /events | - | List events (paginated, filterable) |
| POST | /events | User | Create event |
| GET | /events/{id} | - | Event detail |
| GET | /events/{id}/provenance | - | Data lineage |
| PATCH | /events/{id} | Owner/Admin | Update event |
| DELETE | /events/{id} | Owner/Admin | Delete event |
| GET | /events/{id}/stats | - | RSVP statistics |
| POST | /events/{id}/rsvps | User | Create RSVP |
| GET | /events/{id}/rsvps | - | List RSVPs |
| DELETE | /events/{id}/rsvps/{rid} | User | Delete RSVP |
| POST | /attendees | User | Register attendee |
| GET | /attendees/{id} | - | Attendee detail |
| GET | /attendees/{id}/events | - | Attendee's events |
| GET | /analytics/events/seasonality | - | Monthly distribution |
| GET | /analytics/events/trending | - | Trending events |
| GET | /events/recommendations | User | Personalised recs |
| POST | /admin/imports/run | Admin | Trigger import |
| GET | /admin/imports | Admin | Import history |
| GET | /admin/dataset/meta | Admin | Dataset metadata |
| GET | /admin/imports/quality | Admin | Import analytics |

Full documentation: [docs/API_DOCUMENTATION.pdf](docs/API_DOCUMENTATION.pdf)

---

*Built with AI assistance – See [docs/GENAI_EXPORT_LOGS.pdf](docs/GENAI_EXPORT_LOGS.pdf) for disclosure*
