# GenAI Conversation Export Logs

**Module:** COMP3011 – Web Services and Web Data  
**Student:** Nathaniel Sebastian (sc232ns)  
**Date:** 5th February 2026  
**Tools Used:** Google Gemini (Antigravity), Claude (Anthropic), ChatGPT (OpenAI)

---

## Summary of AI Usage

| Tool | Purpose | Sessions |
|------|---------|----------|
| **Google Gemini** | Coding, debugging, test generation, architecture exploration, security hardening | 10 |
| **Claude** | Documentation polish, refactoring review | 2 |
| **ChatGPT** | Early brainstorming, alternative exploration | 1 |

**Test Count:** 39 tests passing (verified on clean environment via `pytest -q`)

---

## Session 1: Architecture Planning

**Date:** 3 February 2026  
**Tool:** Google Gemini  

### Prompt:
> I need to build a REST API for event management as coursework. What's the best architecture approach for FastAPI + SQLAlchemy?

### AI Response (Summary):
Suggested a layered architecture:
- Routes layer for HTTP handling
- CRUD layer for business logic
- Models for database entities
- Schemas for Pydantic validation

Recommended separating concerns so routes are thin and logic is testable in CRUD.

### My Decision:
Adopted this approach. Created `app/api/routes.py`, `app/crud.py`, `app/models.py`, `app/schemas.py`.

---

## Session 2: RSVP Data Model Design (Alternative Exploration)

**Date:** 3 February 2026  
**Tool:** Google Gemini  

### Prompt:
> Should I store RSVPs as a list embedded in the Event model, or as a separate table?

### AI Response (Summary):
Explained trade-offs:
- **Embedded:** Simpler queries, no JOINs, but no uniqueness constraint
- **Separate table:** Enables UNIQUE(event_id, attendee_id), timestamps, independent queries

Recommended separate table for relational integrity.

### My Decision:
Chose separate `rsvps` table with UNIQUE(event_id, attendee_id) constraint. This enabled proper cascade deletes and duplicate prevention—critical for data integrity.

**Why this matters (creative reasoning):** The embedded approach would have been faster to implement but would have required application-level uniqueness checks, introducing race conditions.

---

## Session 3: Authentication Approach (Alternative Exploration)

**Date:** 3 February 2026  
**Tool:** Google Gemini  

### Prompt:
> JWT vs server-side sessions for a REST API authentication?

### AI Response (Summary):
- **JWT:** Stateless, simpler for pure APIs, no session storage needed
- **Sessions:** Enable immediate revocation, require Redis/DB storage

For coursework scope, JWT simplicity outweighs revocation limitations.

### My Decision:
Implemented JWT with 30-minute expiry. Documented revocation as a known limitation.

**Trade-off rationale:** For a coursework project without Redis infrastructure, JWT's stateless nature aligns with REST principles and simplifies deployment on Render.

---

## Session 4: SQLite Migration Issue

**Date:** 4 February 2026  
**Tool:** Google Gemini  

### Prompt:
> Alembic migration fails with "Cannot add a NOT NULL column with default value NULL" on SQLite

### AI Response:
SQLite doesn't support ALTER TABLE for certain operations. Use Alembic's `batch_alter_table` context manager which recreates the table.

### Code Fix:
```python
with op.batch_alter_table('events') as batch_op:
    batch_op.add_column(sa.Column('source_id', sa.Integer(), nullable=True))
```

### Outcome:
Migration succeeded. Applied this pattern to all subsequent migrations.

---

## Session 5: Test Fixture Design

**Date:** 4 February 2026  
**Tool:** Google Gemini  

### Prompt:
> Tests are interfering with each other. How do I isolate database state?

### AI Response:
Use in-memory SQLite with `StaticPool` and create/drop tables per test function.

### My Enhancement:
Adopted the pattern. All 39 tests now run in <1.5 second with complete isolation.

---

## Session 6: Analytics Implementation

**Date:** 4 February 2026  
**Tool:** Google Gemini  

### Prompt:
> How should I implement a trending score for events?

### AI Response:
Suggested formula weighting recent activity higher:
```
score = (recent_rsvps × 1.5) + (total_rsvps × 0.5)
```

### My Implementation:
Adopted the formula. Added `window_days` parameter to control "recent" definition. Tested in `tests/test_analytics.py`.

---

## Session 7: Security Hardening - RBAC & Rate Limiting

**Date:** 5 February 2026  
**Tool:** Google Gemini  

### Prompt:
> I need to add admin-only routes and rate limiting. What's the cleanest approach?

### AI Response (Summary):
- **RBAC:** Add `is_admin` boolean to User model; create `get_current_admin_user` dependency that checks the flag.
- **Rate Limiting:** In-memory approach using a dict with timestamps; suitable for single-process dev, document Redis as production upgrade.

### Trade-off Discussion:
AI explained that Redis-backed rate limiting is production-grade but adds infrastructure complexity. For coursework demonstration, in-memory is acceptable if documented as a limitation.

### My Implementation:
- Added `is_admin` to User model with Alembic migration
- Created `get_current_admin_user` dependency in `auth.py`
- Implemented `RateLimiter` class in `middleware.py`
- Added tests for 403 and 429 responses

---

## Session 8: ETag and Conditional GET (Research-Informed Feature)

**Date:** 5 February 2026  
**Tool:** Google Gemini  

### Prompt:
> I want to add HTTP caching to demonstrate understanding of REST standards. What's the cleanest approach?

### AI Response (Summary):
Recommended ETag + If-None-Match for conditional GET:
- Compute SHA256 hash of response body
- Set `ETag: "<hash>"` header on 200 responses
- Check `If-None-Match` header; return 304 if matches
- 304 must have no body but include ETag and other headers

Referenced RFC 7232 for correct behavior.

### Why This is "Outstanding" (Creative Reasoning):
ETag caching is not required by the brief but demonstrates:
1. Understanding of HTTP semantics beyond basic CRUD
2. Bandwidth optimization for mobile clients
3. Standards compliance (RFC 7232)

### My Implementation:
- Middleware intercepts GET responses, computes ETag
- 304 responses include `X-Request-ID` and security headers
- Added 3 tests: ETag generation, 304 behavior, mismatch returns 200

---

## Session 9: Error Sanitization

**Date:** 5 February 2026  
**Tool:** Google Gemini  

### Prompt:
> My admin import endpoint leaks exception details. How do I sanitize errors?

### AI Response:
Remove try/catch that exposes `str(e)`. Let exceptions bubble to middleware which returns:
```json
{"detail": "Internal Server Error", "request_id": "<uuid>"}
```

Ensure stack trace is logged server-side with `logging.exception()`.

### My Implementation:
- Removed `detail=str(e)` from admin.py
- Middleware catch-all logs exception with `exc_info=True`
- Added test that mocks failure and verifies no sensitive data in response

---

## Session 10: Documentation Polish

**Date:** 5 February 2026  
**Tool:** Claude  

### Purpose:
Review and improve technical report structure for examiner readability.

### AI Contribution:
Suggested compliance checklist at the start, Mermaid diagrams for architecture/ERD, and explicit references.

### My Modifications:
- Added measured metrics (test runtime, import throughput)
- Ensured all claims match actual code behavior
- Cross-checked consistency: 39 tests across all docs

---

## Critical Reflection

### What AI Did Well
- **Boilerplate generation:** Rapidly scaffolded FastAPI routes and Pydantic schemas
- **Trade-off explanation:** Clearly articulated RSVP storage, auth, and rate limiting alternatives
- **Standards knowledge:** Provided RFC-compliant ETag implementation guidance
- **Debugging:** Quickly identified missing imports and SQLite migration issues

### Where AI Failed (and I Fixed It)

| Failure | Impact | My Fix |
|---------|--------|--------|
| Omitted `requests` from requirements.txt | `ModuleNotFoundError` on clean install | Added dependency manually |
| Generated placeholder test (`pass`) | False test coverage | Rewrote with real assertions |
| Suggested deprecated `Query(regex=...)` | FastAPI deprecation warning | Changed to `Query(pattern=...)` |
| Circular imports (models ↔ schemas) | Import errors | Used string forward references |

### Validation Steps Taken
1. **Clean install test:** `rm -rf venv && python -m venv venv && pip install -r requirements.txt`
2. **Full test suite:** `pytest -q` → 39 passed
3. **Manual curl flows:** Register → Login → Create Event → RSVP → Analytics
4. **Admin RBAC check:** Non-admin gets 403, admin gets 200
5. **ETag check:** First GET returns ETag, second GET with If-None-Match returns 304

### Conclusion
AI accelerated development of standard patterns by ~3× but introduced integration bugs requiring manual verification. Every AI suggestion was reviewed before commit. The "clean install test" caught the most critical failure (missing dependency).

---

## Appendix: Example Prompts

**Prompt 1 (Architecture):**
> "I need to build a REST API for event management as coursework. What's the best architecture approach for FastAPI + SQLAlchemy?"

**Prompt 2 (Alternative Exploration):**
> "Should I store RSVPs as a list embedded in the Event model, or as a separate table?"

**Prompt 3 (Security Trade-off):**
> "JWT vs server-side sessions for a REST API authentication?"

**Prompt 4 (Research Curiosity):**
> "I want to add HTTP caching to demonstrate understanding of REST standards. What's the cleanest approach?"

---

*Exported for COMP3011 CW1 submission – 5th February 2026*
