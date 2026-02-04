# GenAI Conversation Export Logs

**Module:** COMP3011 – Web Services and Web Data  
**Student:** Nathaniel Sebastian (sc232ns)  
**Tools Used:** Google Gemini (Antigravity), ChatGPT (GPT-4)  

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

## Session 2: RSVP Data Model Design

**Date:** 3 February 2026  
**Tool:** Google Gemini  

### Prompt:
> Should I store RSVPs as a list embedded in the Event model, or as a separate table?

### AI Response (Summary):
Explained trade-offs:
- Embedded: Simpler queries, no JOINs
- Separate table: Enables uniqueness constraints, timestamps, independent queries

Recommended separate table for relational integrity.

### My Decision:
Chose separate `rsvps` table with UNIQUE(event_id, attendee_id) constraint. This enabled proper cascade deletes and RSVP history tracking.

---

## Session 3: Authentication Choice

**Date:** 3 February 2026  
**Tool:** Google Gemini  

### Prompt:
> JWT vs server-side sessions for a REST API authentication?

### AI Response (Summary):
- JWT: Stateless, simpler for pure APIs, no session storage needed
- Sessions: Enable immediate revocation, require Redis/DB storage

For coursework scope, JWT simplicity outweighs revocation limitations.

### My Decision:
Implemented JWT with 30-minute expiry. Documented revocation as a known limitation.

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
Use in-memory SQLite with `StaticPool` and create/drop tables per test function:

```python
@pytest.fixture(scope="function")
def db(engine):
    Base.metadata.create_all(bind=engine)
    yield session
    Base.metadata.drop_all(bind=engine)
```

### My Enhancement:
Added transaction rollback for faster cleanup. All 25 tests now run in <1 second.

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

Explained that 1.5× multiplier rewards events gaining momentum.

### My Implementation:
Adopted the formula. Added `window_days` parameter to control "recent" definition.

---

## Session 7: Timezone Bug Fix

**Date:** 4 February 2026  
**Tool:** Google Gemini  

### Prompt:
> Error in analytics.py: NameError: name 'timezone' is not defined

### AI Response:
Missing import. Add `timezone` to the datetime import:
```python
from datetime import datetime, timedelta, timezone
```

### Outcome:
Fixed. Tests continue to pass.

---

## Session 8: PDF Generation

**Date:** 4 February 2026  
**Tool:** Google Gemini  

### Problem:
Coursework requires PDF documentation, but pandoc/weasyprint have missing dependencies.

### Solution Found:
Use Puppeteer (Node.js) to convert HTML to PDF:
```javascript
const page = await browser.newPage();
await page.goto(htmlPath);
await page.pdf({path: outputPath, format: 'A4'});
```

### Outcome:
Generated `docs/API_DOCUMENTATION.pdf` (542KB) and `TECHNICAL_REPORT.pdf` (310KB).

---

## Summary of AI Usage

| Task | AI Contribution | My Contribution |
|------|-----------------|-----------------|
| Architecture | Suggested layered design | Adapted to project needs |
| RSVP model | Explained trade-offs | Made final decision |
| Auth | Compared JWT vs sessions | Chose JWT, documented limits |
| Migrations | Fixed SQLite issue | Applied to all migrations |
| Testing | Fixture pattern | Enhanced with rollbacks |
| Analytics | Scoring formula | Implemented with params |
| Debugging | Identified imports | Applied fixes |

**Total AI-assisted sessions:** 8  
**Human review applied to all suggestions**

---

*Exported for COMP3011 CW1 submission*
