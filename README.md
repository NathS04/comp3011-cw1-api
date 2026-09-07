# EventHub — Production-Style Event & RSVP API

> **Backend engineering project built around production concerns rather than CRUD alone.** EventHub is a FastAPI REST API with **24 REST endpoints**, JWT authentication, role-based access control, PostgreSQL support, Leeds City Council data ingestion, provenance tracking, security controls, CI and **84 automated tests at ~95% coverage**.

`Python` · `FastAPI` · `PostgreSQL` · `Alembic` · `JWT` · `REST API` · `Data Lineage` · `Pytest` · `Render`

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com)
[![CI](https://github.com/NathS04/comp3011-cw1-api/actions/workflows/ci.yml/badge.svg)](https://github.com/NathS04/comp3011-cw1-api/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-84%20passing-brightgreen.svg)](#running-tests)
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)](#running-tests)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 20-second project view

| Dimension | Details |
| :--- | :--- |
| **Problem** | Build a maintainable event-management API with authentication, granular resource ownership, external-data ingestion and analytics. |
| **Backend** | FastAPI + PostgreSQL/SQLite + Alembic migration engine. |
| **Security** | JWT Bearer tokens, PBKDF2-SHA256 hashing, RBAC, owner/admin access control, rate limiting, security headers, defused XML. |
| **API Architecture** | 24 REST endpoints covering events, attendees, RSVPs, analytics, auth and administrative dataset imports. |
| **Testing & Quality** | 84 automated tests at ~95% coverage, clean Ruff linting, MyPy type checking, Bandit security scanning. |
| **Live Deployment** | [comp3011-cw1-api.onrender.com/docs](https://comp3011-cw1-api.onrender.com/docs) (Swagger UI interactive documentation). |

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

export DATABASE_URL="sqlite:///./app.db" SECRET_KEY="dev-key-change-me"
alembic upgrade head
pytest -q                    # Expected: 84 passed
uvicorn app.main:app --reload
```

### Running Test Suite & Quality Gates

```bash
pytest -q                    # 84 tests, <2s runtime
pytest --cov=app             # 95% test coverage
ruff check .                 # Static linting
bandit -r app scripts -q     # Security code scanner
```

---

## Deployment (Render)

**Live Interactive Documentation:** [https://comp3011-cw1-api.onrender.com/docs](https://comp3011-cw1-api.onrender.com/docs)

- `render.yaml` defines the infrastructure-as-code deployment on Render.
- Managed PostgreSQL database backed by Alembic migration scripts.
- *Note:* Free tier spins down after 15 minutes of inactivity; initial cold-start request may take 30-60 seconds.

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

- [Policy Copilot](https://github.com/NathS04/policy_copilot_submission) — Audit-Ready RAG with Citation Enforcement & Evaluation Harness
- [Ledger Data Quality](https://github.com/NathS04/ledger-data-quality) — Python + SQL Financial Data Controls & Reconciliation Pipeline
- [Search Engine Tool](https://github.com/NathS04/comp3011-cw2-api) — Web Crawler, Positional Inverted Index & TF-IDF Ranking Engine

