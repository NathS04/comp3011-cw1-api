# EventHub – Presentation Slides Outline

**COMP3011 CW1 – 5 minutes + 5 mins Q&A**

---

## Slide 1: Title

**EventHub: Event & RSVP API**

- Nathaniel Sebastian (sc232ns)
- COMP3011 Web Services and Web Data
- 5th February 2026
- Live: comp3011-cw1-api.onrender.com

---

## Slide 2: Problem & Solution

**Problem:** Student societies need event registration management

**Solution:**
- RESTful API with JWT authentication
- Full CRUD for Events, Attendees, RSVPs
- Real-world data integration + Analytics
- Production-grade security

---

## Slide 3: Architecture

```
Client → Middleware (RateLimit, Headers, ETag) → FastAPI → Auth → Routes → CRUD → SQLAlchemy → DB
```

**Key Design:**
- Layered architecture
- SQLite (dev) / PostgreSQL (prod)
- Middleware handles cross-cutting concerns

---

## Slide 4: Outstanding Evidence

| Feature | Evidence |
|---------|----------|
| **41 tests passing** | `pytest -q` |
| **RBAC** | `/admin/*` → 403 for non-admin |
| **Rate limiting** | 120/min global, 10/min login → 429 with `request_id` |
| **Security headers** | 7 headers on all responses (X-Request-ID, nosniff, DENY, Referrer, Permissions, CORP, Cache-Control) |
| **ETag caching** | If-None-Match → 304 empty body |
| **Error sanitization** | 500s show generic message + request_id only |
| **Provenance** | SHA256 hash in ImportRun |

---

## Slide 5: Novel Data Integration

**Leeds City Council XML:**
- Real-world XML parsing
- SHA256 provenance hashing
- Idempotent imports

**Analytics:**
- `/analytics/events/seasonality`
- `/analytics/events/trending`
- `/events/recommendations`

---

## Slide 6: Security Model

| Feature | Implementation |
|---------|---------------|
| RBAC | `is_admin` flag; 403 on admin routes |
| Rate Limiting | 120/min global, 10/min login |
| Request Tracing | X-Request-ID on all responses |
| Security Headers | nosniff, DENY, Referrer-Policy, Permissions-Policy, CORP, no-store |
| ETag | Conditional GET, 304 |
| Error Sanitization | No stack traces |

---

## Slide 7: Trade-offs

| Decision | Trade-off |
|----------|-----------|
| In-memory rate limiting | Single-process (Redis for prod) |
| ETag via body hash | Recomputes per request (vs DB timestamp) |
| JWT without refresh | 30-min hard limit |
| Sanitized 500s | Less debug info (but request_id for logs) |

---

## Slide 8: Testing

**41 tests:** Auth, Events, RSVPs, Analytics, Admin, RBAC, Middleware, ETag, Headers, Errors

- In-memory SQLite isolation
- <1.5s runtime

---

## Slide 9: Deliverables

| Item | Location |
|------|----------|
| GitHub | github.com/NathS04/comp3011-cw1-api |
| Live API | comp3011-cw1-api.onrender.com |
| API Docs | docs/API_DOCUMENTATION.pdf |
| Report | TECHNICAL_REPORT.pdf |
| Slides | docs/PRESENTATION_SLIDES.pptx |
| GenAI Logs | docs/GENAI_EXPORT_LOGS.pdf |

---

## Slide 10: GenAI Usage

**Tools:** Gemini, Claude, ChatGPT

**Uses:** Architecture, debugging, security hardening

**Failures Caught:** Missing dep, placeholder tests, deprecated syntax, header flow

---

## Slide 11: Viva Preparation

| Question | Answer |
|----------|--------|
| **Why JWT?** | Stateless, no Redis needed, 30-min expiry |
| **Why in-memory rate limit?** | Acceptable for coursework; Redis for horizontal scaling |
| **How does ETag work?** | SHA256 of body → If-None-Match → 304 empty body |
| **How is RBAC enforced?** | `is_admin` flag; `get_current_admin_user` dependency → 403 |
| **How to promote admin?** | `python scripts/make_admin.py username` |
| **Why X-Request-ID?** | Tracing; included in 500/429 JSON for log correlation |
| **How prevent error leakage?** | No `detail=str(e)`; middleware sanitizes, logs full trace server-side |
| **Why this dataset?** | Real XML parsing, provenance, beyond CSV |
| **What headers on 429?** | X-Request-ID, nosniff, DENY, Referrer-Policy, Permissions-Policy, CORP, no-store |
| **How is 304 tested?** | `tests/test_etags.py` asserts empty body, ETag header present |
| **What AI got wrong?** | Missing `requests`, placeholder tests, header ordering |
| **What's the test count?** | 41 passed |

---

## Slide 12: Thank You

**Questions?**

- Live: comp3011-cw1-api.onrender.com/docs
- Email: sc232ns@leeds.ac.uk

---

*COMP3011 CW1 – 5th February 2026*
