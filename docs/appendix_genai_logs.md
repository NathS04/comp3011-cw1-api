# Appendix: GenAI Conversation Logs

**Purpose:** Selected excerpts demonstrating AI-assisted development for COMP3011 CW1.

---

## 1. Architecture Planning

**Prompt (Me):**
> I need to build a REST API for event management with RSVPs for coursework. What's a good project structure for FastAPI?

**AI Response (Summary):**
> For a FastAPI project of this scope, I recommend a layered architecture:
> - `app/main.py` - Application entry point
> - `app/api/routes.py` - HTTP endpoint handlers  
> - `app/models.py` - SQLAlchemy ORM models
> - `app/schemas.py` - Pydantic request/response models
> - `app/crud.py` - Database operations
> - `app/core/` - Configuration, auth, middleware
>
> This separation keeps your routes thin and your business logic testable...

**My Decision:** Adopted this structure. It aligned with FastAPI best practices and made testing straightforward.

---

## 2. Exploring Design Alternatives: RSVP Storage

**Prompt (Me):**
> Should I store RSVPs as a list field embedded in the Event model, or as a separate table?

**AI Response (Summary):**
> Option A (Embedded): Simpler queries, single read. But:
> - Can't enforce uniqueness at DB level
> - Harder to query "all events user X is attending"
> - Data integrity risks
>
> Option B (Separate table): Adds a JOIN but enables:
> - Database-level unique constraint on (event_id, attendee_id)
> - Timestamp tracking per RSVP
> - Independent RSVP queries

**My Decision:** Separate table. The constraint enforcement and queryability outweigh the slight complexity.

**Reflection:** AI helped me think through trade-offs I might have missed if I'd just picked the "simpler" option.

---

## 3. Debugging: Circular Import Error

**Error I Encountered:**
```
ImportError: cannot import name 'get_user_by_username' from 'app.crud'
```

**Prompt (Me):**
> I'm getting a circular import error between auth.py and crud.py. auth.py imports crud.get_user_by_username, but crud.py imports models which seems to cause a cycle.

**AI Response (Summary):**
> Circular imports happen when two modules depend on each other at import time. Solutions:
> 1. Move the import inside the function that needs it (deferred import)
> 2. Restructure to break the dependency
> 3. Use `TYPE_CHECKING` for type hints only
>
> For your case, try moving the import inside `get_current_user`:
> ```python
> async def get_current_user(...):
>     from app.crud import get_user_by_username
>     ...
> ```

**My Decision:** Used local import inside the function. Fixed the issue without restructuring.

---

## 4. SQLite Migration Compatibility

**Error I Encountered:**
```
sqlalchemy.exc.OperationalError: near "ALTER": syntax error
```

**Prompt (Me):**
> Alembic migration fails on SQLite when adding a foreign key. SQLite doesn't support ALTER TABLE for this.

**AI Response (Summary):**
> SQLite has limited ALTER TABLE support. Alembic's `batch_alter_table` context manager handles this by:
> 1. Creating a new table with the desired schema
> 2. Copying data from old table
> 3. Dropping old table and renaming new one
>
> Use this pattern:
> ```python
> with op.batch_alter_table('events') as batch_op:
>     batch_op.add_column(sa.Column('source_id', sa.Integer()))
>     batch_op.create_foreign_key(...)
> ```

**My Decision:** Implemented `batch_alter_table` for SQLite compatibility while maintaining PostgreSQL support.

---

## 5. Test Fixture Design

**Problem:**
> Tests were failing because database state was leaking between tests.

**AI Suggestion:**
> Use session-scoped engine with `StaticPool` but function-scoped sessions. Recreate tables in each test:
> ```python
> @pytest.fixture(scope="function")
> def db():
>     Base.metadata.create_all(bind=engine)
>     yield TestingSessionLocal()
>     Base.metadata.drop_all(bind=engine)
> ```

**My Modification:** Added connection cleanup and dependency override clearing. The AI's pattern worked but I had to adapt it for my specific setup.

---

## 6. Recommendations Algorithm

**Prompt (Me):**
> How can I implement a simple recommendations endpoint without machine learning?

**AI Response (Summary):**
> Deterministic scoring works well for coursework. Consider:
> 1. Location affinity: Recommend events at locations user has attended
> 2. Recency: Prefer upcoming events
> 3. Popularity: Factor in total RSVPs
> 4. Cold start: For new users, return popular upcoming events
>
> This is explainable and reproducible—good for demonstrating the concept.

**My Implementation:** Used location affinity as the primary signal. Returns events at locations the user has previously RSVP'd to. Cold start returns top upcoming events.

---

## 7. Security Review

**AI Initially Suggested:**
```python
SECRET_KEY = "my-secret-key-123"
```

**I Caught This:** The hardcoded secret would be committed to git. Changed to:
```python
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-key")
```

**Reflection:** AI generates working code fast, but security review is my responsibility. This is why I always read generated code before committing.

---

## Summary

| Category | AI Contribution | My Role |
|----------|-----------------|---------|
| Architecture | Suggested structure | Evaluated and adopted |
| Design decisions | Presented alternatives | Made final choices |
| Debugging | Explained errors, suggested fixes | Verified fixes worked |
| Security | Generated initial code | Caught issues in review |
| Testing | Suggested patterns | Adapted for my context |

**Key Takeaway:** AI accelerated development, but critical thinking, code review, and understanding remained my responsibility.

---

*Full conversation logs available on request. This appendix shows representative excerpts.*
