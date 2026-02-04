# EventHub – Event & RSVP API

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A robust REST API for managing events, attendees, and RSVPs. Built for COMP3011 Web Services coursework.

**🔗 Live API:** [comp3011-cw1-api.onrender.com](https://comp3011-cw1-api.onrender.com)  
**📖 Swagger UI:** [comp3011-cw1-api.onrender.com/docs](https://comp3011-cw1-api.onrender.com/docs)

---

## Features

- **JWT Authentication** – Secure token-based access for protected endpoints
- **Full CRUD** – Create, read, update, delete for Events, Attendees, and RSVPs
- **Pagination & Sorting** – Efficient handling of large datasets with `limit`, `offset`, and `sort` params
- **Event Filtering** – Filter by status (upcoming/past), capacity, location, and date range
- **RSVP Statistics** – Real-time counts of going/maybe/not_going with remaining capacity
- **Comprehensive Validation** – Pydantic-powered input validation with meaningful error messages
- **Auto-generated Docs** – Interactive Swagger UI and ReDoc

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Language | Python 3.11 |
| Database | SQLite (dev), PostgreSQL (prod-ready) |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Authentication | JWT (python-jose) |
| Password Hashing | passlib (pbkdf2_sha256) |
| Testing | pytest + TestClient |
| Deployment | Render.com |

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/NathS04/comp3011-cw1-api.git
cd comp3011-cw1-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root (or set environment variables):

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
```

### Database Setup

```bash
# Run migrations
alembic upgrade head
```

### Run the Server

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Access the API

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_events.py
```

The test suite uses an in-memory SQLite database for isolation.

---

## Project Structure

```
comp3011-cw1-api/
├── app/
│   ├── api/
│   │   └── routes.py      # HTTP endpoint handlers
│   ├── core/
│   │   ├── auth.py        # JWT authentication
│   │   ├── config.py      # Environment configuration
│   │   ├── db.py          # Database session management
│   │   └── middleware.py  # Request logging, exception handling
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response models
│   └── crud.py            # Database operations
├── alembic/               # Database migrations
├── tests/                 # Pytest test suite
├── docs/
│   └── API_DOCUMENTATION.md
├── requirements.txt
├── render.yaml            # Render.com deployment config
└── README.md
```

---

## API Overview

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Health check | No |
| `/auth/register` | POST | Register user | No |
| `/auth/login` | POST | Get JWT token | No |
| `/events` | GET | List events | No |
| `/events` | POST | Create event | Yes |
| `/events/{id}` | GET | Get event | No |
| `/events/{id}` | PATCH | Update event | Yes |
| `/events/{id}` | DELETE | Delete event | Yes |
| `/events/{id}/stats` | GET | RSVP statistics | No |
| `/attendees` | POST | Create attendee | Yes |
| `/attendees/{id}` | GET | Get attendee | No |
| `/attendees/{id}/events` | GET | Attendee's events | No |
| `/events/{id}/rsvps` | POST | Create RSVP | Yes |
| `/events/{id}/rsvps` | GET | List RSVPs | No |
| `/events/{id}/rsvps/{id}` | DELETE | Delete RSVP | Yes |

Full documentation: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## Deployment

### Render.com (Current)

The API is deployed on Render.com with automatic deploys from GitHub.

**Configuration (`render.yaml`):**
- Build: `pip install -r requirements.txt && alembic upgrade head`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables (set in Render dashboard):**
- `DATABASE_URL` – PostgreSQL connection string (provided by Render)
- `SECRET_KEY` – Random string for JWT signing
- `ENVIRONMENT` – `production`

### Manual Deployment

For other platforms (Heroku, AWS, etc.):

1. Set environment variables
2. Run `alembic upgrade head` to apply migrations
3. Start with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` |
| `SECRET_KEY` | JWT signing key | *(development key)* |
| `ENVIRONMENT` | `development` or `production` | `development` |

> ⚠️ **Security:** Never commit `.env` files or real secrets to version control.

---

## Documentation

| Document | Description |
|----------|-------------|
| [API Documentation](docs/API_DOCUMENTATION.md) | Full endpoint reference with examples |
| [Technical Report](TECHNICAL_REPORT_DRAFT.md) | Design decisions, architecture, testing |
| [Swagger UI](https://comp3011-cw1-api.onrender.com/docs) | Interactive API explorer |

---

## Known Limitations

- **SQLite concurrency** – SQLite doesn't handle concurrent writes well; PostgreSQL recommended for production
- **No role-based access** – All authenticated users have equal permissions
- **Token expiry** – 30-minute expiry with no refresh mechanism
- **No email verification** – Users can register with any email

---

## Future Improvements

- [ ] PostgreSQL for production database
- [ ] Event capacity enforcement (reject RSVPs when full)
- [ ] Email notifications for RSVPs
- [ ] Rate limiting
- [ ] Role-based permissions (admin vs. regular user)
- [ ] Event search with full-text matching

---

## License

This project was created for COMP3011 coursework at the University of Leeds.

---

## Author

**Nathaniel Sebastian**  
sc232ns@leeds.ac.uk  
University of Leeds, School of Computing
