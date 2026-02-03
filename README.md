# COMP3011 CW1 - Event RSVP API

A robust REST API for managing events, attendees, and RSVPs. Built with FastAPI, SQLAlchemy, and SQLite.

## Features

- **Authentication**: JWT-based secure access.
- **CRUD Operations**: Complete management of Events, Attendees, and RSVPs.
- **Advanced Features**: Pagination, Sorting, and RSVP statistics.
- **Robust Testing**: Comprehensive test suite with 90%+ coverage.
- **Documentation**: Human-readable API docs and Swagger UI.

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Start Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access API:**
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Documentation

Full API documentation is available in [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (Development)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Testing**: Pytest
- **Auth**: OAuth2 + JWT (python-jose, passlib)

## Architecture

This project follows a layered architecture:
- `app/api`: Route handlers (Controllers)
- `app/crud`: Database logic (Services)
- `app/models`: Database tables (Entities)
- `app/schemas`: Data validation (DTOs)
- `app/core`: Configuration and Auth

## Deployment

Designed for easy deployment on **PythonAnywhere**. See `wsgi.py` for entry point.
