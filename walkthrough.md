# COMP3011 Coursework 1 - Project Walkthrough

**Project:** EventHub - Event & RSVP Management API  
**Status:** 100% Complete ✅  
**Tests:** 25/25 Passing  
**Deployment:** Live on Render.com  

---

## 1. What Was Built

A production-ready RESTful API for event management with the following features:

### Core CRUD Operations
- **Events**: Create, read, update, delete with filtering, pagination, and sorting
- **Attendees**: Registration with unique email constraint
- **RSVPs**: Link attendees to events with status tracking (going/maybe/not_going)
- **Statistics**: Real-time capacity and RSVP breakdown per event

### Authentication
- JWT-based authentication using python-jose
- Secure password hashing with pbkdf2_sha256
- Protected routes for all write operations

### Novel Features (Beyond CRUD)
- **Data Provenance**: `data_sources` and `import_runs` tables track external data imports
- **Analytics Endpoints**:
  - `/analytics/events/seasonality` - Monthly event aggregation
  - `/analytics/events/trending` - RSVP-based trending score
  - `/events/recommendations` - Personalised suggestions based on history

---

## 2. Verification

### Test Results
```bash
$ pytest -q
.........................                              [100%]
25 passed, 2 warnings in 0.72s
```

### Manual Verification Steps
1. Start server: `uvicorn app.main:app --reload`
2. Visit: `http://127.0.0.1:8000/docs` (Swagger UI)
3. **POST** `/auth/register` - Create a user
4. **POST** `/auth/login` - Get JWT token
5. Click **Authorize** button and paste token
6. **POST** `/events` - Create an event
7. **POST** `/attendees` - Register an attendee
8. **POST** `/events/{id}/rsvps` - Create RSVP
9. **GET** `/events/{id}/stats` - View statistics
10. **GET** `/analytics/events/trending` - View analytics

---

## 3. Deployment

### Platform: Render.com
- **URL**: [comp3011-cw1-api.onrender.com](https://comp3011-cw1-api.onrender.com)
- **Auto-deploy**: Push to `main` branch triggers automatic build
- **Config**: `render.yaml` specifies build and start commands

### Environment Variables
| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `ENVIRONMENT` | Set to `production` |

---

## 4. Repository Structure

```
comp3011-cw1-api/
├── app/
│   ├── api/          # Route handlers
│   ├── core/         # Auth, config, middleware
│   ├── models.py     # SQLAlchemy ORM models
│   ├── schemas.py    # Pydantic validation schemas
│   ├── crud.py       # Database operations
│   └── main.py       # FastAPI application
├── tests/            # 25 automated tests
├── alembic/          # Database migrations
├── scripts/          # Import utilities
├── docs/             # Documentation
└── requirements.txt
```

---

## 5. Key Files for Markers

| Deliverable | Location |
|-------------|----------|
| **API Documentation** | `docs/API_DOCUMENTATION.pdf` |
| **Technical Report** | `TECHNICAL_REPORT.pdf` |
| **Presentation Slides** | `docs/PRESENTATION_SLIDES.pptx` |
| **GenAI Logs** | `docs/appendix_genai_logs.md` |
| **README** | `README.md` |

---

*Generated for COMP3011 CW1 submission, University of Leeds*
