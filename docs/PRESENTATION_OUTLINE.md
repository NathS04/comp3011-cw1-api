# EventHub – Presentation Slides Outline

**COMP3011 CW1 – Oral Presentation (5 minutes + 5 mins Q&A)**

---

## Slide 1: Title

**EventHub: Event & RSVP API**

- Nathaniel Sebastian (sc232ns)
- COMP3011 Web Services and Web Data
- 5th February 2026

*Live demo: comp3011-cw1-api.onrender.com*

---

## Slide 2: Problem & Solution

**Problem:**
- Student societies need to manage event registrations
- Track RSVPs, capacity, and attendance patterns

**Solution:**
- RESTful API with JWT authentication
- Full CRUD for Events, Attendees, RSVPs
- **Novel:** External data import + Analytics

---

## Slide 3: Architecture Overview

**[INSERT ARCHITECTURE DIAGRAM]**

```mermaid
flowchart LR
    Client --> FastAPI --> Auth --> Routes --> CRUD --> ORM --> DB
```

**Key decisions:**
- Layered architecture (thin routes, fat CRUD)
- SQLite for dev, PostgreSQL for prod
- Pydantic for validation

---

## Slide 4: Data Model (ERD)

**[INSERT ERD DIAGRAM]**

Key entities:
- User, Event, Attendee, RSVP
- **NEW:** DataSource, ImportRun (provenance tracking)

**Invariants:**
- RSVP unique constraint (event_id, attendee_id)
- Event provenance via source_record_id

---

## Slide 5: Novel Data Integration

**What makes this "Outstanding":**

1. **Import pipeline** (`scripts/import_dataset.py`)
   - Reads XML from Leeds City Council
   - Computes SHA256 hash for provenance
   - Logs ImportRun statistics

2. **Idempotent design**
   - Re-running updates existing records
   - Uses source_record_id for deduplication

3. **Provenance tracking**
   - Every imported event links to its source
   - Audit trail in import_runs table

---

## Slide 6: Analytics Endpoints

**Three novel endpoints:**

| Endpoint | Purpose |
|----------|---------|
| `/analytics/events/seasonality` | Monthly event counts |
| `/analytics/events/trending` | Score by recent RSVPs |
| `/events/recommendations` | Personalised suggestions |

**Trending formula:**
```
score = (recent_rsvps × 1.5) + (total_rsvps × 0.5)
```

---

## Slide 7: Live Demo

**Demo flow (if time):**
1. Show Swagger UI at /docs
2. Register → Login → Create event
3. Create attendee → RSVP
4. Show /events/{id}/stats
5. Show /analytics/events/trending
6. Show /events/recommendations

*Backup: Screenshots in slides*

---

## Slide 8: Testing & Quality

**31 tests passing:**
- Auth: 5 tests (register, login, edge cases)
- Events: 7 tests (CRUD, pagination)
- RSVPs: 4 tests (create, duplicate rejection)
- Analytics: 4 tests (seasonality, trending, recommendations)
- Admin/Import: 6 tests (idempotency, provenance)
- Attendees: 5 tests

**Test isolation:**
- In-memory SQLite with StaticPool
- Fresh tables per test

---

## Slide 9: Version Control Evidence

**[INSERT GIT LOG SCREENSHOT]**

**Commit history highlights:**
- 60+ commits showing incremental development
- Meaningful commit messages
- Feature branches for major work

**Example commits:**
- `feat: Add novel data integration tables`
- `fix(deps): Add requests to requirements.txt`
- `test: Implement personalized recommendation assertions`

---

## Slide 10: API Documentation Overview

**Available at:** `docs/API_DOCUMENTATION.pdf`

**Contents:**
- Security model (JWT, password hashing)
- Every endpoint with examples
- Error codes and formats
- End-to-end worked example

**Also:** Interactive Swagger UI at /docs

---

## Slide 11: Technical Report Highlights

**Key sections:**
1. Reproducibility (exact commands)
2. Dataset provenance + licence
3. Architecture + ERD diagrams
4. Design decisions with trade-offs
5. Security model + threat mitigation
6. Evaluation metrics (measured)
7. GenAI usage + failures + corrections

---

## Slide 12: GenAI Usage

**Tools:** Google Gemini (Antigravity), Claude

**How I used AI:**
- Architecture exploration (RSVP table vs embedded)
- Scaffolding and debugging
- Documentation drafting

**Critical evaluation:**
- Caught missing dependency (`requests`)
- Fixed placeholder test logic
- Updated deprecated API usage

*Full logs: docs/GENAI_EXPORT_LOGS.pdf*

---

## Slide 13: Limitations & Future Work

**Current limitations:**
- Single-tenant (no role-based access)
- 30-min token expiry, no refresh
- No rate limiting

**Future roadmap:**
- Add `is_admin` role column
- Integrate `slowapi` for rate limiting
- Celery scheduled imports
- Refresh token implementation

---

## Slide 14: All Deliverables

| Deliverable | Location |
|-------------|----------|
| GitHub Repo | github.com/NathS04/comp3011-cw1-api |
| Live API | comp3011-cw1-api.onrender.com |
| API Docs (PDF) | docs/API_DOCUMENTATION.pdf |
| Technical Report | TECHNICAL_REPORT.pdf |
| Presentation | docs/PRESENTATION_SLIDES.pptx |
| GenAI Logs | docs/GENAI_EXPORT_LOGS.pdf |

---

## Slide 15: Viva Preparation (Q&A Cheat Sheet)

| Question | Answer |
|----------|--------|
| **Why JWT over sessions?** | Stateless suits REST; no Redis needed; 30-min expiry mitigates risk |
| **How does idempotency work?** | `source_record_id` unique constraint; upsert logic updates existing |
| **How does trending scoring work?** | `(recent_rsvps × 1.5) + (total_rsvps × 0.5)` |
| **What would you change for production?** | PostgreSQL, role-based access, rate limiting, refresh tokens |
| **How did AI help?** | Architecture exploration, scaffolding—always reviewed before commit |
| **What did AI get wrong?** | Missing `requests` dep, placeholder test, deprecated Query usage |
| **Why this dataset?** | Real-world XML, requires parsing/normalization, proves integration skill |
| **How do you prevent duplicate RSVPs?** | UNIQUE(event_id, attendee_id) constraint at DB level |
| **What's your security posture?** | PBKDF2 passwords, JWT HS256, Pydantic validation, param queries |
| **How did you test?** | 31 tests, in-memory SQLite, function-scoped fixtures, <1s runtime |

---

## Slide 16: Thank You

**Questions?**

- Live API: comp3011-cw1-api.onrender.com
- Swagger: /docs
- Contact: sc232ns@leeds.ac.uk

---

*Presentation outline for COMP3011 CW1 – 5th February 2026*
