# EventHub — Event and RSVP API

> A University of Leeds coursework project demonstrating a FastAPI backend with authentication, resource ownership, event and RSVP management, external-data imports and provenance. The repository contains 24 REST endpoints and an automated test suite. This is an academic portfolio project, not a deployed client service.

[Portfolio — Future](https://future-nathaniel.pages.dev/) · [About Nathaniel Sebastian](https://github.com/NathS04)


`Python` · `FastAPI` · `PostgreSQL` · `Alembic` · `JWT` · `REST API` · `Data Lineage` · `Pytest` · `Render`

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com)
[![CI](https://github.com/NathS04/comp3011-cw1-api/actions/workflows/ci.yml/badge.svg)](https://github.com/NathS04/comp3011-cw1-api/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 20-second project view

| Dimension | Details |
| :--- | :--- |
| **Problem** | Build a maintainable event-management API with authentication, granular resource ownership, external-data ingestion and analytics. |
| **Backend** | FastAPI + PostgreSQL/SQLite + Alembic migration engine. |
| **Security** | JWT Bearer tokens, PBKDF2-SHA256 hashing, RBAC, owner/admin access control, rate limiting, security headers, defused XML. |
| **API Architecture** | 24 REST endpoints covering events, attendees, RSVPs, analytics, auth and administrative dataset imports. |
| **Testing & Quality** | CI runs pytest with coverage, Ruff, mypy and Bandit. The recorded 7 September 2026 run passed all 84 tests; use the CI badge for current status. |
| **Run and inspect** | Run locally using the quickstart; interactive API documentation is served at `/docs`. Render deployment configuration is included in `render.yaml`. |

---

## Engineering Decisions

- **Resource Ownership & RBAC:** Access control is enforced at both entity and role levels. `created_by_user_id` protects event modifications, while RSVP operations check owner, attendee, or admin privileges.
- **Dialect-Aware Analytics:** SQL analytics queries (monthly seasonality, trending events) use dialect abstraction to run seamlessly on both SQLite (local development) and PostgreSQL (production).
- **Data Provenance Tracking:** `GET /events/{id}/provenance` returns full data lineage records for ingested external events (source dataset, batch timestamp, import status).
- **Safe External Ingestion:** Parser uses `defusedxml` to protect against XML External Entity (XXE) vulnerabilities when ingesting Leeds City Council public XML feeds.
- **Conditional Caching & ETags:** Responses support SHA256 body hash ETags with `If-None-Match` validation, returning HTTP `304 Not Modified` to reduce server payload.
- **Production Security & Error Sanitisation:** Middleware attaches UUID `X-Request-ID` headers to all responses and catches uncaught exceptions to output sanitized 500 error objects without exposing stack traces.

---

## Key Features & Endpoints

| Category | Method & Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST /auth/register`<br>`POST /auth/login` | None | User registration and JWT token issuance |
| **Events** | `GET /events`<br>`POST /events`<br>`GET /events/{id}`<br>`PATCH /events/{id}`<br>`DELETE /events/{id}` | Mixed | Paginated filtering, CRUD with strict owner/admin access control |
| **Provenance** | `GET /events/{id}/provenance` | None | Full data lineage and source tracking for ingested datasets |
| **RSVPs** | `POST /events/{id}/rsvps`<br>`GET /events/{id}/rsvps`<br>`DELETE /events/{id}/rsvps/{rid}` | Authenticated | Attendee reservation and status management |
| **Analytics** | `GET /analytics/events/seasonality`<br>`GET /analytics/events/trending`<br>`GET /events/recommendations` | Mixed | Event popularity stats, monthly distribution, and user recommendations |
| **Admin Imports** | `POST /admin/imports/run`<br>`GET /admin/imports`<br>`GET /admin/imports/quality` | Admin | Ingestion runner, batch status history, and data-quality metrics |

---

## Security Controls Matrix

| Feature | Implementation Detail |
| :--- | :--- |
| **Authentication** | JWT Bearer (HS256, 30-min expiry) |
| **Password Hashing** | PBKDF2-SHA256 via Passlib |
| **RBAC** | Anonymous (read), Authenticated (CRUD), Admin (imports) |
| **Rate Limiting** | 120 req/min global, 10 req/min login endpoint |
| **Security Headers** | `X-Request-ID`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `CORP` |
| **XML Safety** | `defusedxml` protection against XXE attacks |

---

## Quickstart & Verification

```bash
git clone https://github.com/NathS04/comp3011-cw1-api.git && cd comp3011-cw1-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

export DATABASE_URL="sqlite:///./app.db" SECRET_KEY="dev-key-change-me"
alembic upgrade head
pytest -q                    # See the test output for the current count
uvicorn app.main:app --reload
```

### Running Test Suite & Quality Gates

```bash
pytest -q
pytest --cov=app --cov-report=term-missing
ruff check .                 # Static linting
mypy app scripts/import_dataset.py scripts/make_admin.py scripts/clean_db.py
bandit -c pyproject.toml -r app scripts -q     # Security code scanner
```

---

## Deployment (Render)

`render.yaml` describes a Render deployment with PostgreSQL and Alembic migrations. A currently available public demo has not been verified. Use the local quickstart to inspect the API and its `/docs` page.

---

## Academic & Coursework Deliverables

This project was originally submitted for COMP3011 Web Services at the University of Leeds (2025/26).

| Deliverable | Format | Location |
| :--- | :--- | :--- |
| **Technical Report** | PDF | [TECHNICAL_REPORT.pdf](TECHNICAL_REPORT.pdf) |
| **API Documentation** | PDF | [docs/API_DOCUMENTATION.pdf](docs/API_DOCUMENTATION.pdf) |
| **Verification Guide** | Markdown | [VERIFICATION_INSTRUCTIONS.md](VERIFICATION_INSTRUCTIONS.md) |
| **Presentation Slides** | PPTX | [docs/PRESENTATION_SLIDES.pptx](docs/PRESENTATION_SLIDES.pptx) |

---

## Related Portfolio Work

- [Policy Copilot](https://github.com/NathS04/policy_copilot_submission) — Academic policy-question-answering prototype with evidence checks and evaluation
- [Ledger Data Quality](https://github.com/NathS04/ledger-data-quality) — Python + SQL Financial Data Controls & Reconciliation Pipeline
- [Search Engine Tool](https://github.com/NathS04/comp3011-cw2-api) — Web Crawler, Positional Inverted Index & TF-IDF Ranking Engine

