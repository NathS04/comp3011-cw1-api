# COMP3011 Technical Report: EventHub – Event & RSVP API

---

**Module:** COMP3011 – Web Services and Web Data  
**Coursework:** CW1 – Individual Web Services API Development  
**Student:** Nathaniel Sebastian (sc232ns)  
**Date:** 4th February 2026  

**GitHub Repository:** [github.com/NathS04/comp3011-cw1-api](https://github.com/NathS04/comp3011-cw1-api)  
**Live API:** [comp3011-cw1-api.onrender.com](https://comp3011-cw1-api.onrender.com)  
**API Documentation:** See `docs/API_DOCUMENTATION.md`  

---

## 1. Introduction & Problem Statement

### 1.1 Problem Domain

This project addresses the need for a lightweight backend service to manage event registrations. The imagined use case is a **student society events platform** where organisers can create events (socials, workshops, talks) and track RSVPs from members. The system needs to handle the core workflow: creating events with limited capacity, registering attendees, and recording their responses (going, maybe, not going).

This is a common pattern in real-world applications—from Eventbrite-style ticketing to internal corporate event management. Building a clean API for this domain demonstrates understanding of relational data modelling, authentication, and RESTful design principles.

### 1.2 Functional Requirements

The API must support the following operations:

- **Events**: Create, read, update, and delete events with title, description, location, start/end times, and capacity.
- **Attendees**: Register attendees with name and unique email address.
- **RSVPs**: Link attendees to events with a status (`going`, `maybe`, `not_going`).
- **Uniqueness**: Enforce one RSVP per attendee per event (no duplicate registrations).
- **Statistics**: Provide a summary endpoint showing RSVP counts and remaining capacity.
- **Authentication**: Protect write operations with JWT-based authentication.

### 1.3 Non-Functional Requirements

- RESTful JSON API following HTTP semantics (proper status codes, resource-based URLs).
- SQL database with version-controlled migrations (Alembic).
- External deployment (Render.com).
- Automated test suite with isolated test database.
- Clear separation of concerns (models, schemas, CRUD, routes, configuration).
- Comprehensive API documentation.

### 1.4 GenAI Context

This assessment permits the use of Generative AI tools. I used AI assistance throughout development as a "pair programmer"—for brainstorming architecture, generating boilerplate, and debugging issues. Section 7 provides a detailed declaration and critical reflection on this usage.

---

## 2. Technology Stack & Architecture

### 2.1 Stack Selection

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Language** | Python 3.11 | Familiar, excellent library ecosystem, strong typing support. |
| **Framework** | FastAPI | Modern async framework with automatic OpenAPI docs, Pydantic validation, and dependency injection. Chosen over Django REST Framework for its lighter footprint and native async support. |
| **Database** | SQLite | Simple file-based database, ideal for development and coursework. No external database server required. |
| **ORM** | SQLAlchemy 2.x | Industry-standard ORM with excellent relationship handling. The 2.x API provides cleaner type hints via `Mapped` annotations. |
| **Migrations** | Alembic | Pairs naturally with SQLAlchemy; enables version-controlled schema changes. |
| **Authentication** | JWT (python-jose) | Stateless tokens fit REST principles. Simpler than session-based auth for a pure API. |
| **Password Hashing** | passlib (pbkdf2_sha256) | Secure, NIST-approved algorithm. I initially tried bcrypt but encountered a library compatibility issue on my environment, so I migrated to pbkdf2_sha256. |
| **Testing** | pytest + TestClient | FastAPI's TestClient provides synchronous access to async endpoints. In-memory SQLite with `StaticPool` ensures test isolation. |
| **Deployment** | Render.com | Free tier, easy GitHub integration, supports ASGI (Uvicorn). |

**Trade-off note:** SQLite lacks concurrency support for high-traffic production use, but for a coursework project demonstrating API design, it's perfectly adequate and simplifies local development.

### 2.2 Architecture Overview

The project follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                               │
│                (Postman / Swagger UI / Frontend)            │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP Request
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    app/main.py                              │
│              (FastAPI app, middleware, CORS)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  app/api/routes.py                          │
│         (HTTP handlers, auth dependencies, validation)      │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌───────────────────┐           ┌───────────────────┐
│  app/schemas.py   │           │   app/core/auth   │
│  (Pydantic DTOs)  │           │   (JWT, hashing)  │
└───────────────────┘           └───────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     app/crud.py                             │
│            (Business logic, database operations)            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    app/models.py                            │
│              (SQLAlchemy ORM model definitions)             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      SQLite Database                        │
│                        (app.db)                             │
└─────────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**

- **Routes are thin**: Handlers validate input, call CRUD functions, and return responses. No business logic lives in routes.
- **CRUD layer is reusable**: Database operations are isolated in `crud.py`, making them testable and reusable.
- **Schemas separate concerns**: Pydantic models define what the API accepts (input) and returns (output), independent of database models.
- **Configuration via environment**: Secrets (`SECRET_KEY`, `DATABASE_URL`) are loaded from environment variables, never hardcoded.

---

## 3. Data Model & API Design

### 3.1 Entity-Relationship Model

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │    events    │       │  attendees   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ username     │       │ title        │       │ name         │
│ email        │       │ description  │       │ email (UQ)   │
│ hashed_pw    │       │ location     │       └──────┬───────┘
│ created_at   │       │ start_time   │              │
└──────────────┘       │ end_time     │              │
                       │ capacity     │              │
                       │ created_at   │              │
                       └──────┬───────┘              │
                              │                      │
                              │    ┌─────────────┐   │
                              └────┤    rsvps    ├───┘
                                   ├─────────────┤
                                   │ id (PK)     │
                                   │ event_id (FK)│
                                   │ attendee_id (FK)│
                                   │ status      │
                                   │ created_at  │
                                   └─────────────┘
                                   UNIQUE(event_id, attendee_id)
```

**Design decisions:**

- **RSVP as a junction table**: Rather than a simple many-to-many, RSVP carries its own data (`status`, `created_at`). This allows tracking *when* someone RSVP'd and *what* their response was.
- **Status as a string enum**: Using `going`, `maybe`, `not_going` as string values provides flexibility while being easily validated via Pydantic `Literal` types.
- **Unique constraint on (event_id, attendee_id)**: Prevents duplicate RSVPs at the database level, ensuring integrity even if application logic fails.

### 3.2 API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Liveness check | No |
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Obtain JWT token | No |
| GET | `/events` | List events (paginated, filterable) | No |
| POST | `/events` | Create event | **Yes** |
| GET | `/events/{id}` | Get event details | No |
| PATCH | `/events/{id}` | Update event | **Yes** |
| DELETE | `/events/{id}` | Delete event | **Yes** |
| GET | `/events/{id}/stats` | Get RSVP statistics | No |
| POST | `/attendees` | Register attendee | **Yes** |
| GET | `/attendees/{id}` | Get attendee details | No |
| GET | `/attendees/{id}/events` | List events for attendee | No |
| POST | `/events/{id}/rsvps` | Create RSVP | **Yes** |
| GET | `/events/{id}/rsvps` | List RSVPs for event | No |
| DELETE | `/events/{id}/rsvps/{rsvp_id}` | Cancel RSVP | **Yes** |

### 3.3 Notable Endpoint: Event Statistics

The `/events/{id}/stats` endpoint demonstrates derived data computation:

```json
{
  "event_id": 1,
  "going": 45,
  "maybe": 12,
  "not_going": 3,
  "remaining_capacity": 40
}
```

This aggregates RSVP data and calculates `remaining_capacity = capacity - going_count`. It's useful for organisers to quickly assess event demand without manually counting RSVPs.

---

## 4. Implementation Highlights & Challenges

### 4.1 Key Implementation Choices

**JWT Authentication Flow**

I implemented OAuth2 password flow using FastAPI's `OAuth2PasswordBearer` dependency. The login endpoint accepts form data (per OAuth2 spec) and returns a JWT. Protected routes use a `get_current_user` dependency that:

1. Extracts the token from the `Authorization` header
2. Decodes and validates the JWT signature
3. Fetches the user from the database
4. Raises 401 if any step fails

This approach keeps route handlers clean—they simply declare `current_user: User = Depends(get_current_user)`.

**Database Session Management**

Each request gets its own database session via FastAPI's dependency injection:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

The `yield` pattern ensures the session is always closed, even if an exception occurs. This prevents connection leaks and maintains database integrity.

**Input Validation**

Pydantic handles all input validation declaratively. For example, `EventCreate` uses:
- `Field(min_length=1, max_length=200)` for title
- `Field(ge=1)` for capacity (must be positive)
- A `model_validator` to ensure `end_time > start_time`

This moves validation logic out of route handlers and makes it testable in isolation.

### 4.2 Challenges & Solutions

**Challenge 1: Alembic + In-Memory SQLite Conflict**

Initially, running tests caused Alembic migrations to fail because the in-memory database was created fresh for each test, but Alembic expected a persistent file. 

*Solution*: I configured tests to use `StaticPool` with `check_same_thread=False`, which keeps a single in-memory database alive for the test session. The `conftest.py` fixture creates all tables directly using `Base.metadata.create_all()` instead of running migrations.

**Challenge 2: Circular Imports in Auth Module**

The `auth.py` module needed to import `crud.get_user_by_username`, but `crud.py` imported models that indirectly depended on auth. This caused import errors at startup.

*Solution*: I moved the `get_user` helper function inside `get_current_user` with a local import: `from app.crud import get_user_by_username`. This defers the import until runtime, breaking the circular dependency.

**Challenge 3: N+1 Query Problem in Stats Endpoint**

The initial stats implementation loaded the event, then issued separate queries for each RSVP. For events with many RSVPs, this was inefficient.

*Solution*: I used SQLAlchemy's `joinedload` option to eagerly load RSVPs in a single query:

```python
db.query(Event).options(joinedload(Event.rsvps)).filter(Event.id == event_id).first()
```

This reduced the stats endpoint from O(n) queries to O(1).

---

## 5. Testing Strategy & Evidence

### 5.1 Testing Approach

The test suite uses **pytest** with FastAPI's `TestClient`. Key characteristics:

- **Isolated database**: An in-memory SQLite database is created for each test session using `StaticPool`.
- **Fresh state per test**: Fixtures drop and recreate all tables before each test function, ensuring no state leakage.
- **Both happy and unhappy paths**: Tests verify successful operations *and* proper error responses (401, 404, 409, 422).

### 5.2 Test Coverage

The suite includes **20+ test cases** covering:

| Category | What's Tested |
|----------|---------------|
| **Health** | `/health` returns 200 and `{"ok": true}` |
| **Auth** | Registration, login, wrong password, non-existent user, accessing protected routes without token |
| **Events** | Create, list (with pagination), get by ID, update, delete, 404 for missing events |
| **Attendees** | Create, get by ID, list events for attendee |
| **RSVPs** | Create, list for event, delete, duplicate RSVP rejection (409) |
| **Stats** | Correct counts for going/maybe/not_going, remaining capacity calculation |

### 5.3 Example Test

```python
def test_create_rsvp_duplicate_rejected(client: TestClient, auth_headers):
    # Create event and attendee first
    event = client.post("/events", json={...}, headers=auth_headers).json()
    attendee = client.post("/attendees", json={...}, headers=auth_headers).json()
    
    # First RSVP succeeds
    response = client.post(f"/events/{event['id']}/rsvps", 
                           json={"attendee_id": attendee["id"], "status": "going"},
                           headers=auth_headers)
    assert response.status_code == 201
    
    # Duplicate RSVP returns 409 Conflict
    response = client.post(f"/events/{event['id']}/rsvps",
                           json={"attendee_id": attendee["id"], "status": "maybe"},
                           headers=auth_headers)
    assert response.status_code == 409
    assert "duplicate" in response.json()["detail"].lower()
```

This test verifies the database constraint is correctly mapped to a user-friendly HTTP error.

---

## 6. Limitations & Future Work

### 6.1 Current Limitations

- **Single-tenant design**: All users can modify all events. A production system would need role-based access control (e.g., only event creators can edit their events).
- **No email verification**: Users can register with any email; there's no verification flow.
- **SQLite concurrency**: SQLite doesn't handle concurrent writes well. High-traffic production would require PostgreSQL.
- **Basic statistics only**: The stats endpoint provides counts but no historical trends or advanced analytics.
- **Token expiry is short**: JWT tokens expire after 30 minutes with no refresh mechanism.

### 6.2 Future Improvements

- **PostgreSQL migration**: Add a `DATABASE_URL` for Postgres in production while keeping SQLite for local development.
- **Event search & filtering**: Add query parameters like `?q=tech&location=leeds&start_after=2026-03-01`.
- **RSVP capacity enforcement**: Reject RSVPs with `status=going` when capacity is reached.
- **Email notifications**: Send confirmation emails when RSVPs are created.
- **Rate limiting**: Prevent abuse with request throttling.
- **Public dataset integration**: Import real event data (e.g., from Leeds cultural events API) to demonstrate analytics capabilities.

---

## 7. Generative AI Usage & Reflection

### 7.1 Tools Used

| Tool | Purpose |
|------|---------|
| **Google Gemini Pro (Antigravity Agent)** | Primary development assistant—architecture planning, code generation, debugging, documentation drafting. |
| **ChatGPT (GPT-4)** | Secondary assistant for marking feedback and documentation structure advice. |

### 7.2 Workflow

My development process integrated AI throughout:

1. **Planning phase**: I described the brief requirements and asked the AI to suggest a project structure. It proposed the layered architecture (routes → crud → models) which I adopted.

2. **Scaffolding**: I used AI to generate initial boilerplate—Pydantic schemas, SQLAlchemy models, basic CRUD functions. This saved significant typing time.

3. **Iterative refinement**: I wrote tests first (sometimes with AI assistance on syntax), then asked the AI to implement features to make tests pass. I reviewed all generated code before committing.

4. **Debugging**: When encountering errors (e.g., Alembic migration issues, JWT decode failures), I pasted tracebacks and asked for explanations and fixes.

5. **Documentation**: I used AI to help structure this report and draft initial sections, then edited extensively for accuracy and voice.

### 7.3 Benefits & Risks

**Benefits:**

- **Speed**: Generating boilerplate (schemas, models) that would take hours to type manually took minutes.
- **Learning**: Seeing AI-suggested patterns (like `StaticPool` for test isolation) taught me techniques I hadn't encountered before.
- **Exploration**: I could quickly prototype alternative designs (e.g., "what if RSVP was embedded in Event?") to compare approaches.

**Risks & Mitigations:**

- **Hallucinations**: The AI occasionally suggested imports that didn't exist or used deprecated APIs. *Mitigation*: I always ran the code and fixed errors manually.
- **Security blind spots**: Early AI-generated auth code used a hardcoded secret key. *Mitigation*: I caught this in code review and refactored to use environment variables.
- **Over-reliance**: Accepting code without understanding it leads to untraceable bugs. *Mitigation*: I ensured I could explain every line before committing.

**Concrete bugs from AI suggestions:**

1. The AI initially suggested using `bcrypt` for password hashing, but my environment had a library conflict. I spent time debugging before switching to `pbkdf2_sha256`.
2. An AI-generated test fixture didn't properly isolate database state, causing flaky tests. I had to redesign the fixture to use session-scoped engines.

### 7.4 Alignment with Assessment Criteria

My use of Generative AI aligns with the brief's "high-level use" category:

> "High-level use of GenAI to aid creative thinking and solution exploration, exploring high-level alternatives and reimagining cutting-edge solutions."

I used AI not just to write code, but to:
- Explore architectural alternatives before committing to a design
- Generate and compare multiple implementation approaches
- Critically evaluate suggestions rather than accepting them blindly
- Document the process transparently in this reflection

The appendix contains selected conversation logs demonstrating this exploratory usage.

---

## Appendix A: Selected GenAI Conversation Logs

*See attached `appendix_genai_logs.pdf` for full conversation excerpts.*

**Example excerpt (Architecture Planning):**

> **Me**: I need to build a REST API for event management with RSVPs. What's a good project structure for FastAPI?
>
> **AI**: For a FastAPI project of this scope, I'd recommend a layered architecture:
> - `app/main.py` - Application entry point
> - `app/api/routes.py` - HTTP endpoint handlers
> - `app/models.py` - SQLAlchemy ORM models
> - `app/schemas.py` - Pydantic request/response models
> - `app/crud.py` - Database operations
> - `app/core/` - Configuration, auth, middleware
>
> This separation keeps your routes thin and your business logic testable...

---

**Word Count:** ~2,200 words (excluding diagrams and code snippets)
