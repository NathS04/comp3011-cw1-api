# Appendix A: GenAI Conversation Logs

**Module:** COMP3011 – Web Services and Web Data  
**Student:** Nathaniel Sebastian (sc232ns)  

This appendix contains selected excerpts from conversations with Generative AI tools used during the development of the EventHub API. These logs demonstrate how AI was used for architecture planning, debugging, and code refinement—not just copying generated code.

---

## 1. Architecture Planning

**Date:** Early January 2026  
**Tool:** Google Gemini Pro (via Antigravity Agent)

### Conversation Excerpt

**Me:**
> I need to build a REST API for event management with RSVPs for my COMP3011 coursework. The brief says I need Events, Attendees, and RSVPs with authentication. What's a good project structure for FastAPI?

**AI:**
> For a FastAPI project of this scope, I'd recommend a layered architecture that separates concerns clearly:
> 
> ```
> app/
> ├── main.py          # Application entry point
> ├── api/
> │   └── routes.py    # HTTP endpoint handlers
> ├── models.py        # SQLAlchemy ORM models
> ├── schemas.py       # Pydantic request/response models
> ├── crud.py          # Database operations
> └── core/
>     ├── config.py    # Environment configuration
>     ├── db.py        # Database session
>     └── auth.py      # JWT authentication
> ```
> 
> This separation keeps your routes thin—they handle HTTP concerns only—while business logic lives in `crud.py`. It also makes testing easier since you can test CRUD functions independently of HTTP.

**My Reflection:**
I adopted this structure with minor modifications. The layered approach proved valuable when I needed to add the stats endpoint later—I could add to `crud.py` without touching the route handler logic.

---

## 2. Debugging: bcrypt Installation Issue

**Date:** Mid-January 2026  
**Tool:** Google Gemini Pro

### Conversation Excerpt

**Me:**
> I'm getting this error when trying to run my FastAPI app:
> ```
> ImportError: cannot import name 'Crypto' from 'Crypto'
> ```
> I installed bcrypt for password hashing but it's not working.

**AI:**
> This looks like a conflict between the `pycryptodome` and `pycrypto` packages. However, for your use case (password hashing), I'd recommend using `passlib` instead of direct bcrypt.
> 
> `passlib` provides a high-level interface and handles the complexity for you:
> 
> ```python
> from passlib.hash import pbkdf2_sha256
> 
> # Hash a password
> hashed = pbkdf2_sha256.hash("password123")
> 
> # Verify a password
> pbkdf2_sha256.verify("password123", hashed)  # Returns True
> ```
> 
> `pbkdf2_sha256` is NIST-approved and doesn't have the native compilation issues that bcrypt sometimes has on certain systems.

**My Reflection:**
I initially wanted to use bcrypt because it's commonly used in tutorials, but the dependency issues were frustrating. Switching to `pbkdf2_sha256` via passlib solved the problem and taught me that there are multiple secure hashing algorithms—bcrypt isn't the only option.

---

## 3. Test Isolation Problem

**Date:** Late January 2026  
**Tool:** Google Gemini Pro

### Conversation Excerpt

**Me:**
> My pytest tests are failing intermittently. Sometimes `test_list_events` passes, sometimes it fails because it finds events from other tests. I think the database isn't being reset between tests.

**AI:**
> You're right—this is a common issue with database tests. The problem is likely that your in-memory SQLite database is being shared across tests.
> 
> For proper isolation, you need to:
> 
> 1. Use `StaticPool` to ensure all connections use the same in-memory database:
> 
> ```python
> from sqlalchemy.pool import StaticPool
> 
> engine = create_engine(
>     "sqlite:///:memory:",
>     connect_args={"check_same_thread": False},
>     poolclass=StaticPool
> )
> ```
> 
> 2. Create and drop tables in a fixture:
> 
> ```python
> @pytest.fixture
> def db():
>     Base.metadata.create_all(bind=engine)
>     yield SessionLocal()
>     Base.metadata.drop_all(bind=engine)
> ```
> 
> The `drop_all` ensures each test starts with a clean slate.

**My Reflection:**
This was one of the most frustrating bugs I encountered. Tests would pass individually but fail when run together. The AI's explanation of `StaticPool` was key—I didn't fully understand Python's connection pooling before this.

---

## 4. Schema Validation Design

**Date:** Late January 2026  
**Tool:** ChatGPT (GPT-4)

### Conversation Excerpt

**Me:**
> I want to validate that an event's end_time is after its start_time in my Pydantic schema. How do I do that?

**AI:**
> Pydantic v2 uses `model_validator` for cross-field validation. Here's how to do it:
> 
> ```python
> from pydantic import BaseModel, model_validator
> 
> class EventCreate(BaseModel):
>     title: str
>     start_time: datetime
>     end_time: datetime
> 
>     @model_validator(mode="after")
>     def validate_times(self):
>         if self.end_time <= self.start_time:
>             raise ValueError("end_time must be after start_time")
>         return self
> ```
> 
> The `mode="after"` means the validator runs after individual field validation, so you can be sure both fields are valid datetimes before comparing them.

**My Reflection:**
I initially tried to do this validation in the route handler, but moving it to the schema makes more sense—it's validated automatically on every request, and the error message is consistent.

---

## 5. Security Review

**Date:** February 2026  
**Tool:** Google Gemini Pro

### Conversation Excerpt

**Me:**
> Can you review my auth.py for security issues?
> 
> ```python
> SECRET_KEY = "comp3011-coursework-secret-key"
> ALGORITHM = "HS256"
> 
> def create_access_token(data: dict):
>     to_encode = data.copy()
>     expire = datetime.utcnow() + timedelta(minutes=30)
>     to_encode.update({"exp": expire})
>     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
> ```

**AI:**
> I see a security issue: your `SECRET_KEY` is hardcoded. This is problematic because:
> 
> 1. It's visible in version control
> 2. It can't be rotated without code changes
> 3. It's the same across all environments
> 
> You should load it from an environment variable:
> 
> ```python
> import os
> SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-fallback-key")
> ```
> 
> Also, consider using `datetime.now(timezone.utc)` instead of `datetime.utcnow()`, which is deprecated in Python 3.12+.

**My Reflection:**
This was an important catch. I originally used a hardcoded key because I saw it in a tutorial, but the AI correctly pointed out why this is bad practice. I immediately refactored to use environment variables.

---

## 6. Documentation Structure

**Date:** February 2026  
**Tool:** ChatGPT (GPT-4)

### Conversation Excerpt

**Me:**
> I'm writing my technical report for COMP3011. What sections should it have to hit the distinction band?

**AI:**
> Based on typical coursework marking criteria for a distinction (80-100%), your report should demonstrate:
> 
> 1. **Clear problem understanding** – Introduction with requirements
> 2. **Justified technical choices** – Why FastAPI over Django, why SQLite, etc.
> 3. **Sound architecture** – Diagrams showing layers and data flow
> 4. **Implementation depth** – Not just "what" but "why" and "alternatives considered"
> 5. **Testing evidence** – What you tested and how
> 6. **Critical reflection** – Limitations, future work, lessons learned
> 7. **GenAI transparency** – How you used AI and what you learned from it
> 
> The key differentiator for distinction is showing *engineering thinking*—trade-offs, alternatives, and decisions—not just describing what you built.

**My Reflection:**
This helped me structure my report. I made sure each section included not just descriptions but justifications and trade-off discussions.

---

## Summary of AI Usage

| Category | Purpose | Tools Used |
|----------|---------|------------|
| Architecture | Project structure, layering patterns | Gemini Pro |
| Debugging | Dependency issues, test isolation | Gemini Pro |
| Code Generation | Initial boilerplate, validators | Gemini Pro, GPT-4 |
| Code Review | Security review, best practices | Gemini Pro |
| Documentation | Report structure, API doc format | GPT-4 |

**Total time saved estimate:** 8-12 hours of research and debugging.

**Key learning:** AI is most useful for exploring alternatives and debugging—not for replacing understanding. I still had to read every line of generated code and understand why it worked.

---

*End of Appendix A*
