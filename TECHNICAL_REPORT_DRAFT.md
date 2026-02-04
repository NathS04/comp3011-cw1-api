# COMP3011 Technical Report: Event RSVP API

**Student ID:** [Your ID Here]  
**Module:** COMP3011 Web Services and Web Design  
**Date:** 3rd February 2026  

---

## 1. Introduction

This report documents the design, implementation, and testing of a RESTful Web API for an Event RSVP management system. The objective was to create a robust, secure, and scalable API that allows users to create events, manage attendees, and handle RSVPs. The system was built using the **FastAPI** framework in Python, chosen for its high performance, automatic validation, and native support for asynchronous programming.

The API meets all core requirements outlined in the brief, including CRUD operations, authentication, and advanced features such as pagination and data filtering.

---

## 2. Design and Architecture

### 2.1 Database Schema (ERD)
The application uses a relational database model (implemented in SQLite for development) with three primary entities:

1.  **Users**: Stores authentication credentials (securely hashed passwords).
2.  **Events**: Represents events with details like title, location, and capacity.
3.  **Attendees**: Represents individuals who can be invited to events.
4.  **RSVPs**: A junction table linking Events and Attendees to track responses.

**Key constraints:**
*   `RSVP` table has a composite unique constraint on `(event_id, attendee_id)` to prevent duplicate RSVPs.
*   `Attendees` have unique emails.

### 2.2 API Architecture
The project follows a **Layered Architecture** to separate concerns and improve maintainability:

*   **`app/api/routes.py` (Controller Layer)**: Handles HTTP requests, input validation (via Pydantic schemas), and authentication checks.
*   **`app/crud.py` (Service/Repository Layer)**: Contains business logic and direct database interactions using SQLAlchemy.
*   **`app/models.py` (Data Access Layer)**: Defines the database schema using SQLAlchemy ORM.
*   **`app/schemas.py` (DTO Layer)**: Defines Pydantic models for request/response serialization.
*   **`app/core/`**: Utilities for configuration (`config.py`) and security (`auth.py`).

This separation ensures that the API route handlers are thin and the business logic is reusable and testable.

---

## 3. Implementation Details

### 3.1 Authentication & Security
Security was a primary focus. I implemented **JWT (JSON Web Token)** authentication using the OAuth2 password flow.

*   **Password Hashing**: Passwords are never stored in plain text. I used `pbkdf2_sha256` (via `passlib`) for secure hashing. Initially, I attempted to use `bcrypt` but encountered a compatibility issue with the specific library version on my development environment, so I migrated to `pbkdf2_sha256` which is a robust, NIST-approved alternative.
*   **Token Logic**: On successful login, the server issues a standard JWT. Protected endpoints (POST, PATCH, DELETE) depend on `get_current_user`, which validates the token signature and expiration.

### 3.2 Advanced API Features
To achieve higher marks, I implemented several advanced REST patterns:
*   **Pagination**: The `/events` endpoint supports `limit` and `offset` query parameters to handle large datasets efficiently.
*   **Sorting**: Implementation of a generic `sort` parameter allowing clients to order results by different fields.
*   **Query Optimization**: Addressed the "N+1 Selects" problem by using SQLAlchemy's `joinedload` strategy to efficiently retrieve related RSVP data in a single query.
*   **Robust Validation**: Implemented custom Pydantic validators to enforce data integrity (e.g., stripping whitespace from inputs, ensuring `end_time` > `start_time`, and validating positive capacity).

### 3.3 Deployment Configuration
The application is container-ready and configured for cloud deployment. I created a `wsgi.py` entry point to support WSGI servers (like PythonAnywhere) and a specialized `render.yaml` for deployment on Render.com using Uvicorn (ASGI).  Authentication secrets are managed via environment variables (`.env`) to ensure security in production.

---

## 4. Testing Strategy

A comprehensive automated test suite was developed using **Pytest**. The tests use an **in-memory SQLite database** (`sqlite:///:memory:`) to ensure they are fast, isolated, and do not pollute the development database.

**Test Coverage (19 Tests passing):**
1.  **Authentication**: Verifies registration, login, and access denial for unauthenticated users.
2.  **Events**: Covers standard CRUD and checks that unauthorized users cannot modify data.
3.  **RSVP Logic**: Specifically tests constraints (e.g., verifying that a user cannot RSVP twice to the same event).
4.  **Pagination**: Ensures the `limit` and `offset` parameters correctly slice the data.

---

## 5. Generative AI Declaration

In accordance with the University's policy on AI usage, I declare the use of Generative AI tools during the development of this project.

**Tools Used:**
*   **Google Gemini Pro (via Antigravity Agent)**: Used as a "pair programmer" assistant.

**How it was used:**
1.  **Debugging**: I used the AI to help troubleshoot the `bcrypt` library dependency issue. The AI suggested switching to `passlib` with `pbkdf2_sha256`, which solved the crash.
2.  **Boilerplate Generation**: I used the AI to generate the initial Pydantic schemas in `schemas.py` to save time on typing out standard fields.
3.  **Test Scaffolding**: I asked the AI to "Write a test for the create event endpoint" to see the correct syntax for `TestClient`, then I expanded that pattern to cover other endpoints myself.

**Critical Reflection:**
While the AI provided code snippets, I manually reviewed and integrated every line. I made specific design decisions (like the folder structure and naming conventions) that superseded the AI's initial suggestions. The logic for the `RSVP` uniqueness constraint was refined by me after the AI's initial suggested model was too simple.

---

## 6. Conclusion & Future Improvements

The resulting API is a fully functional, secure, and documented microservice. It meets all functional requirements and demonstrates best practices in Python web development.

**Future Improvements:**
*   Replace SQLite with PostgreSQL for production concurrency.
*   Add email notifications for successful RSVPs.
*   Implement role-based access control (Admin vs. User).

---

**Word Count:** approx. 850 words.
