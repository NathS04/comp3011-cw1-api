# COMP3011 Coursework 1: API Documentation

**Author:** Nathaniel Sebastian  
**Module:** Web Services and Web Data (COMP3011)

## Overview

This API allows users to create and manage events, attendees, and RSVPs. It features JWT-based authentication, role-based access control (implied via token), and comprehensive data validation.

**Base URL:** `https://comp3011-cw1-api.onrender.com` (Production)  
**Local URL:** `http://127.0.0.1:8000`

---

## Authentication

All write operations (POST, PATCH, DELETE) require a valid JWT token. Read operations (GET) are public.

### How to Authenticate

1. **Register a User:**
   `POST /auth/register`
   ```json
   {
     "username": "myuser",
     "email": "user@example.com",
     "password": "strongpassword"
   }
   ```

2. **Login:**
   `POST /auth/login` (Form Data)
   - `username`: myuser
   - `password`: strongpassword

   **Response:**
   ```json
   {
     "access_token": "eyJhbG...",
     "token_type": "bearer"
   }
   ```

3. **Use Token:**
   Include the token in the `Authorization` header of subsequent requests:
   `Authorization: Bearer <your_token>`

---

## Endpoints

### 1. Events

| Method | Endpoint | Description | Auth |
|:-------|:---------|:------------|:-----|
| GET | `/events` | List events with pagination and sorting | No |
| POST | `/events` | Create a new event | **Yes** |
| GET | `/events/{id}` | Get event details | No |
| PATCH | `/events/{id}` | Update event details | **Yes** |
| DELETE | `/events/{id}` | Delete an event | **Yes** |
| GET | `/events/{id}/stats` | Get RSVP statistics | No |

#### Example: List Events
`GET /events?limit=5&sort=-start_time`

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Tech Meetup",
      "start_time": "2026-03-23T18:00:00",
      ...
    }
  ],
  "total": 1,
  "limit": 5,
  "offset": 0
}
```

### 2. Attendees

| Method | Endpoint | Description | Auth |
|:-------|:---------|:------------|:-----|
| POST | `/attendees` | Register an attendee | **Yes** |
| GET | `/attendees/{id}` | Get attendee details | **Yes** |

### 3. RSVPs

| Method | Endpoint | Description | Auth |
|:-------|:---------|:------------|:-----|
| POST | `/events/{id}/rsvps` | RSVP to an event | **Yes** |
| GET | `/events/{id}/rsvps` | List RSVPs for an event | No |
| DELETE | `/events/{id}/rsvps/{id}` | Cancel an RSVP | **Yes** |

---

## Error Codes

| Code | Meaning |
|:-----|:--------|
| 200 | OK - Success |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - invalid data |
| 401 | Unauthorized - Missing or invalid token |
| 404 | Not Found - Resource does not exist |
| 409 | Conflict - Duplicate entry (e.g. duplicate RSVP) |
| 422 | Validation Error - Invalid input format |
| 500 | Internal Server Error - Unexpected failure |
