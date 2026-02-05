# EventHub API Documentation

**Version:** 1.3.0  
**Author:** Nathaniel Sebastian (sc232ns@leeds.ac.uk)  
**Last Updated:** 5th February 2026  

---

## Table of Contents

1. [Base URLs](#base-urls)
2. [Security Model](#security-model)
3. [Response Headers](#response-headers)
4. [Authentication](#authentication)
5. [Events](#events)
6. [Attendees](#attendees)
7. [RSVPs](#rsvps)
8. [Analytics & Recommendations](#analytics--recommendations)
9. [Admin & Dataset Management](#admin--dataset-management)
10. [Error Handling](#error-response-format)
11. [Running Locally](#running-locally)

---

## Base URLs

| Environment | URL |
|-------------|-----|
| **Production** | `https://comp3011-cw1-api.onrender.com` |
| **Local Development** | `http://127.0.0.1:8000` |

**Interactive Documentation:**
- Swagger UI: `/docs`
- ReDoc: `/redoc`

---

## Security Model

### Authentication
All endpoints that modify data require a valid JWT token in the `Authorization` header.

| Mechanism | Implementation |
|-----------|----------------|
| **Token Type** | JWT (JSON Web Token) |
| **Algorithm** | HS256 |
| **Expiry** | 30 minutes |
| **Header Format** | `Authorization: Bearer <token>` |

### Password Security
- Hashed with PBKDF2-SHA256 (via `passlib`)
- Plaintext passwords never stored

### Authorization Levels (RBAC)
| Role | Capabilities |
|------|--------------|
| **Anonymous** | Read events, attendees, analytics |
| **Authenticated User** | Create/update/delete events, RSVPs, attendees |
| **Admin** | Dataset import, view import logs |

> **Important:** Admin endpoints (`/admin/*`) require the `is_admin` flag to be `True` on the user account. Non-admin users receive `403 Forbidden`.

### Rate Limiting
| Scope | Limit | Response |
|-------|-------|----------|
| Global | 120 requests/minute | `429 Too Many Requests` |
| `/auth/login` | 10 requests/minute | `429 Too Many Requests` |

Rate limit responses include `request_id` in JSON body and `X-Request-ID` header.

---

## Response Headers

**All responses include:**

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Request-ID` | UUID v4 | Request tracing and correlation |
| `X-Content-Type-Options` | `nosniff` | MIME type sniffing prevention |
| `X-Frame-Options` | `DENY` | Clickjacking protection |

**Auth/Admin endpoints additionally include:**

| Header | Value |
|--------|-------|
| `Cache-Control` | `no-store` |

**GET requests (200 OK) include:**

| Header | Value | Purpose |
|--------|-------|---------|
| `ETag` | `"<sha256-hash>"` | Conditional GET support |

### Conditional GET (ETag)

Clients can use the `If-None-Match` header to avoid re-downloading unchanged data:

```bash
# First request - get ETag
curl -i http://127.0.0.1:8000/events
# Response includes: ETag: "abc123..."

# Subsequent request - use ETag
curl -H "If-None-Match: \"abc123...\"" http://127.0.0.1:8000/events
# Response: 304 Not Modified (no body)
```

**304 Response includes:** `ETag`, `X-Request-ID`, security headers (no body).

---

## Authentication

Most endpoints that modify data (POST, PATCH, DELETE) require a valid JWT token.

### Auth Flow Summary

```
1. POST /auth/register  →  Create account
2. POST /auth/login     →  Receive JWT token
3. Include token in requests: Authorization: Bearer <token>
```

### Register a New User

**Endpoint:** `POST /auth/register`  
**Auth Required:** No

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "mySecurePassword123"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2026-02-04T12:30:00Z"
}
```

---

### Login

**Endpoint:** `POST /auth/login`  
**Auth Required:** No  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Body (Form Data):**
```
username=johndoe
password=mySecurePassword123
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Events

### List Events

**Endpoint:** `GET /events`  
**Auth Required:** No

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `limit` | integer | Max results (default: 10, max: 100) | `?limit=20` |
| `offset` | integer | Skip N results (default: 0) | `?offset=10` |
| `sort` | string | Sort field, prefix `-` for desc | `?sort=-start_time` |
| `q` | string | Search title (partial match) | `?q=tech` |
| `location` | string | Filter by location | `?location=Leeds` |
| `start_after` | datetime | Events starting after | `?start_after=2026-03-01T00:00:00` |
| `start_before` | datetime | Events starting before | `?start_before=2026-04-01T00:00:00` |
| `min_capacity` | integer | Minimum capacity | `?min_capacity=50` |
| `status` | string | `upcoming` or `past` | `?status=upcoming` |

**Success Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Tech Meetup Leeds",
      "description": "Monthly gathering for tech enthusiasts",
      "location": "Leeds Digital Hub",
      "start_time": "2026-03-15T18:00:00Z",
      "end_time": "2026-03-15T21:00:00Z",
      "capacity": 50,
      "created_at": "2026-02-01T10:00:00Z"
    }
  ],
  "total": 42,
  "limit": 5,
  "offset": 0
}
```

**Response Headers:** `ETag: "<hash>"`, `X-Request-ID: "<uuid>"`

---

### Create Event

**Endpoint:** `POST /events`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "title": "Freshers Welcome Social",
  "description": "Welcome event for new students at Leeds University.",
  "location": "Leeds Student Union, Riley Smith Hall",
  "start_time": "2026-09-25T19:00:00Z",
  "end_time": "2026-09-25T23:00:00Z",
  "capacity": 200
}
```

**Success Response (201 Created):** Returns event object with `id`.

---

### Get Event by ID

**Endpoint:** `GET /events/{id}`  
**Auth Required:** No

**Response Headers:** `ETag: "<hash>"`

---

### Update Event

**Endpoint:** `PATCH /events/{id}`  
**Auth Required:** Yes

**Request Body (partial update):**
```json
{
  "title": "Tech Meetup Leeds 2026",
  "capacity": 75
}
```

---

### Delete Event

**Endpoint:** `DELETE /events/{id}`  
**Auth Required:** Yes

**Success Response:** `204 No Content`

---

## Attendees

### Create Attendee

**Endpoint:** `POST /attendees`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "name": "Alice Smith",
  "email": "alice.smith@leeds.ac.uk"
}
```

**Error:** `409 Conflict` if email already registered.

---

### Get Attendee by ID

**Endpoint:** `GET /attendees/{id}`  
**Auth Required:** No

---

## RSVPs

### Create RSVP

**Endpoint:** `POST /events/{event_id}/rsvps`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "attendee_id": 1,
  "status": "going"
}
```

**Valid status values:** `going`, `maybe`, `not_going`

**Error Responses:**
- `404` – Event or attendee not found
- `409` – Duplicate RSVP (attendee already RSVP'd to this event)

---

## Analytics & Recommendations

### Event Seasonality

**Endpoint:** `GET /analytics/events/seasonality`  
**Auth Required:** No

**Success Response (200 OK):**
```json
{
  "items": [
    {"month": "2026-01", "count": 5, "top_categories": ["General"]},
    {"month": "2026-02", "count": 12, "top_categories": ["General"]}
  ]
}
```

---

### Trending Events

**Endpoint:** `GET /analytics/events/trending`  
**Auth Required:** No

**Trending Score Formula:**
```
score = (recent_rsvps × 1.5) + (total_rsvps × 0.5)
```

---

### Personalised Recommendations

**Endpoint:** `GET /events/recommendations`  
**Auth Required:** Yes

Returns events based on user's RSVP history locations.

---

## Admin & Dataset Management

> **Important:** All `/admin/*` endpoints require the `is_admin` flag to be `True`. Non-admin users receive `403 Forbidden`.

### Trigger Dataset Import

**Endpoint:** `POST /admin/imports/run`  
**Auth Required:** Admin

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/admin/imports/run?source_type=xml" \
  -H "Authorization: Bearer $TOKEN"
```

**Success Response (201 Created):**
```json
{
  "message": "Import finished successfully",
  "source": "https://opendata.leeds.gov.uk/downloads/Licences/temp-event-notice/temp-event-notice.xml"
}
```

---

### List Import Runs

**Endpoint:** `GET /admin/imports`  
**Auth Required:** Admin

---

### Get Dataset Metadata

**Endpoint:** `GET /admin/dataset/meta`  
**Auth Required:** Admin

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

**500 Internal Server Error includes request_id:**
```json
{
  "detail": "Internal Server Error",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Common Failure Modes

| Scenario | HTTP Status | Response Example |
|----------|-------------|------------------|
| **Missing Token** | `401 Unauthorized` | `{"detail": "Not authenticated"}` |
| **Invalid Token** | `401 Unauthorized` | `{"detail": "Could not validate credentials"}` |
| **Non-Admin on /admin/*` | `403 Forbidden` | `{"detail": "The user doesn't have enough privileges"}` |
| **RSVP Conflict** | `409 Conflict` | `{"detail": "duplicate RSVP for this attendee/event"}` |
| **Rate Limited** | `429 Too Many Requests` | `{"detail": "Too Many Requests", "request_id": "<uuid>"}` |
| **Server Error** | `500 Internal Server Error` | `{"detail": "Internal Server Error", "request_id": "<uuid>"}` |

---

## HTTP Status Codes Summary

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET, PATCH |
| `201` | Created | Successful POST |
| `204` | No Content | Successful DELETE |
| `304` | Not Modified | ETag match (If-None-Match) |
| `400` | Bad Request | Invalid data (duplicate username) |
| `401` | Unauthorized | Missing/invalid JWT |
| `403` | Forbidden | Non-admin accessing admin routes |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate entry |
| `422` | Unprocessable Entity | Validation failed |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected error (includes `request_id`) |

---

## Running Locally

### Setup
```bash
git clone https://github.com/NathS04/comp3011-cw1-api.git
cd comp3011-cw1-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///./app.db" SECRET_KEY="your-secret-key"
alembic upgrade head
uvicorn app.main:app --reload
```

### Running Tests
```bash
pytest -v
```

**Result:** 39 tests passing

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.3.0 | 2026-02-05 | Added ETag/304 support, improved 429/500 responses with request_id |
| 1.2.0 | 2026-02-05 | Added RBAC, rate limiting, security headers |
| 1.1.0 | 2026-02-04 | Added analytics and recommendations endpoints |
| 1.0.0 | 2026-02-01 | Initial release |

---

*Document generated for COMP3011 CW1 submission*
