# EventHub API Documentation

**Version:** 1.0.0  
**Author:** Nathaniel Sebastian  
**Last Updated:** 4th February 2026  

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

## Authentication

Most endpoints that modify data (POST, PATCH, DELETE) require a valid JWT token. Read operations (GET) are generally public.

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

**Error Responses:**
- `400 Bad Request` – Username or email already registered
- `422 Unprocessable Entity` – Validation failed (e.g., password too short)

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

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Incorrect username or password"
}
```

---

### Using the Token

Include the token in the `Authorization` header for all protected requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Events

### List Events

**Endpoint:** `GET /events`  
**Auth Required:** No

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max results to return (default: 10) |
| `offset` | integer | Number of results to skip (default: 0) |
| `sort` | string | Field to sort by (prefix with `-` for descending, e.g., `-start_time`) |
| `q` | string | Search by title (partial match) |
| `location` | string | Filter by location (partial match) |
| `start_after` | datetime | Filter events starting after this time |
| `start_before` | datetime | Filter events starting before this time |
| `min_capacity` | integer | Filter events with at least this capacity |
| `status` | string | `upcoming` (future events) or `past` (past events) |

**Example Request:**
```
GET /events?limit=5&sort=-start_time&status=upcoming
```

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
  "total": 1,
  "limit": 5,
  "offset": 0
}
```

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

**Validation Rules:**
- `title`: 1–200 characters, required
- `description`: 0–1000 characters, optional
- `location`: 1–200 characters, required
- `start_time`: ISO 8601 datetime, required
- `end_time`: Must be after `start_time`, required
- `capacity`: Positive integer (≥ 1), required

**Success Response (201 Created):**
```json
{
  "id": 2,
  "title": "Freshers Welcome Social",
  "description": "Welcome event for new students at Leeds University.",
  "location": "Leeds Student Union, Riley Smith Hall",
  "start_time": "2026-09-25T19:00:00Z",
  "end_time": "2026-09-25T23:00:00Z",
  "capacity": 200,
  "created_at": "2026-02-04T14:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` – Missing or invalid token
- `422 Unprocessable Entity` – Validation failed (e.g., `end_time` before `start_time`)

---

### Get Event by ID

**Endpoint:** `GET /events/{id}`  
**Auth Required:** No

**Success Response (200 OK):**
```json
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
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Event not found"
}
```

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

**Success Response (200 OK):**
Returns the updated event object.

**Error Responses:**
- `401 Unauthorized` – Missing or invalid token
- `404 Not Found` – Event does not exist
- `422 Unprocessable Entity` – Validation failed

---

### Delete Event

**Endpoint:** `DELETE /events/{id}`  
**Auth Required:** Yes

**Success Response (204 No Content):**
No body returned.

**Error Responses:**
- `401 Unauthorized` – Missing or invalid token
- `404 Not Found` – Event does not exist

---

### Get Event Statistics

**Endpoint:** `GET /events/{id}/stats`  
**Auth Required:** No

**Success Response (200 OK):**
```json
{
  "event_id": 1,
  "going": 35,
  "maybe": 10,
  "not_going": 5,
  "remaining_capacity": 15
}
```

**Calculation:**
- `remaining_capacity = capacity - going`

**Error Response (404 Not Found):**
```json
{
  "detail": "Event not found"
}
```

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

**Success Response (201 Created):**
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice.smith@leeds.ac.uk"
}
```

**Error Responses:**
- `401 Unauthorized` – Missing or invalid token
- `409 Conflict` – Email already registered

---

### Get Attendee by ID

**Endpoint:** `GET /attendees/{id}`  
**Auth Required:** No

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice.smith@leeds.ac.uk"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Attendee not found"
}
```

---

### Get Events for Attendee

**Endpoint:** `GET /attendees/{id}/events`  
**Auth Required:** No

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Tech Meetup Leeds",
    "start_time": "2026-03-15T18:00:00Z",
    ...
  }
]
```

Returns all events the attendee has RSVP'd to.

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

**Success Response (201 Created):**
```json
{
  "id": 1,
  "event_id": 1,
  "attendee_id": 1,
  "status": "going",
  "created_at": "2026-02-04T15:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` – Missing or invalid token
- `404 Not Found` – Event or attendee does not exist
- `409 Conflict` – Attendee has already RSVP'd to this event

---

### List RSVPs for Event

**Endpoint:** `GET /events/{event_id}/rsvps`  
**Auth Required:** No

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "event_id": 1,
    "attendee_id": 1,
    "status": "going",
    "created_at": "2026-02-04T15:00:00Z"
  },
  {
    "id": 2,
    "event_id": 1,
    "attendee_id": 2,
    "status": "maybe",
    "created_at": "2026-02-04T15:30:00Z"
  }
]
```

---

### Delete RSVP

**Endpoint:** `DELETE /events/{event_id}/rsvps/{rsvp_id}`  
**Auth Required:** Yes

**Success Response (204 No Content):**
No body returned.

**Error Responses:**
- `401 Unauthorized` – Missing or invalid token
- `404 Not Found` – Event or RSVP does not exist

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (422), the response includes field-level details:

```json
{
  "detail": [
    {
      "loc": ["body", "capacity"],
      "msg": "Input should be greater than or equal to 1",
      "type": "greater_than_equal"
    }
  ]
}
```

---

## HTTP Status Codes Summary

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET, PATCH requests |
| `201` | Created | Successful POST (resource created) |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Invalid request data (e.g., duplicate username) |
| `401` | Unauthorized | Missing or invalid JWT token |
| `404` | Not Found | Requested resource doesn't exist |
| `409` | Conflict | Duplicate entry (e.g., RSVP already exists) |
| `422` | Unprocessable Entity | Request body fails Pydantic validation |
| `500` | Internal Server Error | Unexpected server-side error |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider adding throttling to prevent abuse.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-04 | Initial release |
