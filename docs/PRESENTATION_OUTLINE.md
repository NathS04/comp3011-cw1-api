# EventHub – Presentation Slides Outline

**COMP3011 CW1 – Oral Presentation (5 minutes + 5 mins Q&A)**

---

## Slide 1: Title

**EventHub: Event & RSVP API**

- Nathaniel Sebastian (sc232ns)
- COMP3011 Web Services and Web Data
- 4th February 2026

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

**Diagram showing:**
```
Client → FastAPI → Routes → CRUD → SQLAlchemy → Database
                     ↓
              Auth (JWT)
```

**Key decisions:**
- Layered architecture (thin routes, fat CRUD)
- SQLite for dev, PostgreSQL-ready for prod
- Pydantic for validation

---

## Slide 4: Data Model

**ERD showing:**
- Users, Events, Attendees, RSVPs
- **NEW:** DataSource, ImportRun (provenance tracking)

**Highlight:**
- RSVP unique constraint (event_id, attendee_id)
- Event provenance fields (source_id, is_seeded)

---

## Slide 5: Novel Data Integration

**What makes this "Outstanding":**

1. **Import pipeline** (`scripts/import_dataset.py`)
   - Reads CSV from external source
   - Creates DataSource record
   - Logs ImportRun statistics

2. **Idempotent design**
   - Re-running won't duplicate data
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

**25 tests passing:**
- Auth: 6 tests (register, login, edge cases)
- Events: 5 tests (CRUD, pagination)
- RSVPs: 4 tests (create, duplicate rejection)
- Analytics: 4 tests (seasonality, trending, recommendations)

**Test isolation:**
- In-memory SQLite with StaticPool
- Fresh tables per test

---

## Slide 9: Version Control

**Commit history highlights:**
- 60+ commits showing incremental development
- Meaningful commit messages
- Feature branches for major work

**Example commits:**
- "Add novel data integration tables"
- "Implement analytics endpoints"
- "Fix SQLite migration compatibility"

---

## Slide 10: API Documentation

**Available at:** `docs/API_DOCUMENTATION.pdf`

**Contents:**
- Auth flow (register → login → use token)
- Every endpoint with examples
- Error codes and formats
- Demo curl script

**Also:** Interactive Swagger UI at /docs

---

## Slide 11: Technical Report Summary

**Key sections:**
1. Architecture & Data Model
2. Key Design Decisions (3 with alternatives)
3. Novel Data Integration
4. Analytics Methodology
5. Testing Strategy
6. GenAI Usage Declaration

**GenAI highlight:** Used AI to *explore alternatives*, not just generate code

---

## Slide 12: GenAI Usage

**Tools:** Gemini (Antigravity), GPT-4

**How I used AI:**
- Architecture exploration (RSVP table vs embedded)
- Scaffolding and debugging
- Documentation drafting

**Critical evaluation:**
- Caught security issues (hardcoded secrets)
- Fixed environment-specific bugs (bcrypt → pbkdf2)
- Understood every line before committing

---

## Slide 13: Limitations & Future Work

**Current limitations:**
- Single-tenant (no role-based access)
- 30-min token expiry, no refresh
- SQLite concurrency

**Future roadmap:**
- PostgreSQL for production
- Capacity enforcement
- Email notifications
- Rate limiting

---

## Slide 14: All Deliverables

| Deliverable | Location |
|-------------|----------|
| GitHub Repo | github.com/NathS04/comp3011-cw1-api |
| Live API | comp3011-cw1-api.onrender.com |
| API Docs (PDF) | docs/API_DOCUMENTATION.pdf |
| Technical Report | TECHNICAL_REPORT.pdf |
| Presentation | This deck |
| GenAI Logs | docs/appendix_genai_logs.md |

---

## Slide 15: Q&A Preparation

**Likely questions:**

1. **Why JWT over sessions?**
   - Stateless suits REST APIs; no session store needed

2. **How does idempotency work?**
   - source_record_id unique constraint; update if exists

3. **How does trending scoring work?**
   - Recent RSVPs weighted 1.5×, total weighted 0.5×

4. **What would you change for production?**
   - PostgreSQL, role-based access, rate limiting

5. **How did AI help?**
   - Architecture exploration, scaffolding, debugging
   - Always reviewed before committing

---

## Slide 16: Thank You

**Questions?**

- Live API: comp3011-cw1-api.onrender.com
- Swagger: /docs
- Contact: sc232ns@leeds.ac.uk

---

*Presentation outline for COMP3011 CW1*
