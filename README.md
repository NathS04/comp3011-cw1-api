# EventHub – Event & RSVP API

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-25%20passing-brightgreen.svg)](#running-tests)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A REST API for managing events, attendees, and RSVPs with **novel data integration** and **analytics features**. Built for COMP3011 Web Services coursework at the University of Leeds.

---

## Quick Links

| Resource | Link |
|----------|------|
| **🔗 Live API** | [comp3011-cw1-api.onrender.com](https://comp3011-cw1-api.onrender.com) |
| **📖 Swagger UI** | [comp3011-cw1-api.onrender.com/docs](https://comp3011-cw1-api.onrender.com/docs) |
| **📄 API Documentation (PDF)** | [docs/API_DOCUMENTATION.pdf](docs/API_DOCUMENTATION.pdf) |
| **📝 Technical Report** | [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md) |
| **🎤 Presentation Slides** | [docs/PRESENTATION_SLIDES.pdf](docs/PRESENTATION_SLIDES.pdf) |

> **Note for Markers:** Export API_DOCUMENTATION.md to PDF using pandoc: `pandoc docs/API_DOCUMENTATION.md -o docs/API_DOCUMENTATION.pdf`

---

## Features

### Core Functionality
- **JWT Authentication** – Secure token-based access for protected endpoints
- **Full CRUD** – Create, read, update, delete for Events, Attendees, and RSVPs
- **Pagination & Sorting** – `limit`, `offset`, and `sort` params with filtering
- **RSVP Statistics** – Real-time counts of going/maybe/not_going

### Novel Features (Outstanding-Level)
- **📊 Data Integration** – Import external datasets with full provenance tracking
- **📈 Seasonality Analytics** – Event distribution by month
- **🔥 Trending Detection** – Score events by recent RSVP activity
- **🎯 Recommendations** – Personalised event suggestions based on user history

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Language | Python 3.11 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Authentication | JWT (python-jose) |
| Testing | pytest (25 tests) |
| Deployment | Render.com |

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/NathS04/comp3011-cw1-api.git
cd comp3011-cw1-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure
export DATABASE_URL="sqlite:///./app.db"
export SECRET_KEY="your-secret-key"

# Run migrations and start
alembic upgrade head
uvicorn app.main:app --reload
```

Access at: http://127.0.0.1:8000/docs

---

## Running Tests

```bash
pytest -v
```

**Result:** 25 tests passing (auth, events, attendees, RSVPs, analytics, health)

---

## API Endpoints Overview

### Core Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| POST | `/auth/register` | Register user | No |
| POST | `/auth/login` | Get JWT token | No |
| GET/POST | `/events` | List/Create events | GET: No, POST: Yes |
| GET/PATCH/DELETE | `/events/{id}` | Get/Update/Delete event | Yes for mutations |
| GET | `/events/{id}/stats` | RSVP statistics | No |
| POST | `/attendees` | Create attendee | Yes |
| POST | `/events/{id}/rsvps` | Create RSVP | Yes |

### Analytics Endpoints (Novel Features)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/events/seasonality` | Monthly event distribution |
| GET | `/analytics/events/trending` | Trending events by RSVP activity |
| GET | `/events/recommendations` | Personalised suggestions |

Full documentation: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## Project Structure

```
comp3011-cw1-api/
├── app/
│   ├── api/
│   │   ├── routes.py        # Core CRUD endpoints
│   │   └── analytics.py     # Analytics & recommendations
│   ├── core/
│   │   ├── auth.py          # JWT authentication
│   │   ├── config.py        # Environment config
│   │   └── db.py            # Database session
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLAlchemy models (inc. DataSource, ImportRun)
│   ├── schemas.py           # Pydantic schemas
│   └── crud.py              # Business logic
├── scripts/
│   └── import_dataset.py    # Idempotent data import
├── alembic/                 # Database migrations
├── tests/                   # 25 test cases
├── docs/
│   ├── API_DOCUMENTATION.md
│   └── appendix_genai_logs.md
├── TECHNICAL_REPORT.md
└── README.md
```

---

## Data Integration

The system supports importing external event data with provenance tracking:

```bash
python scripts/import_dataset.py
```

**Features:**
- Creates `DataSource` and `ImportRun` records
- Idempotent: re-running won't duplicate data
- Logs errors without stopping import
- Tracks rows read, inserted, updated

---

## Documentation for Submission

| Document | Purpose | Format |
|----------|---------|--------|
| **API Documentation** | Full endpoint reference | [Markdown](docs/API_DOCUMENTATION.md) → Export to PDF |
| **Technical Report** | Design decisions, architecture, GenAI reflection | [Markdown](TECHNICAL_REPORT.md) → Export to PDF |
| **Presentation** | 5-min demo slides | [Outline](docs/PRESENTATION_OUTLINE.md) |
| **GenAI Logs** | Conversation excerpts | [Appendix](docs/appendix_genai_logs.md) |

---

## Deployment Verification

```bash
# Health check
curl https://comp3011-cw1-api.onrender.com/health

# Expected: {"ok": true}
```

---

## Author

**Nathaniel Sebastian**  
sc232ns@leeds.ac.uk  
University of Leeds, School of Computing

---

*Built with ❤️ and AI assistance for COMP3011 CW1*
