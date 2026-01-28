# COMP3011 CW1 API (FastAPI)

Run locally:
  source .venv/bin/activate
  alembic revision --autogenerate -m "init"
  alembic upgrade head
  uvicorn app.main:app --reload

Docs:
  http://127.0.0.1:8000/docs
  http://127.0.0.1:8000/openapi.json

Tests:
  source .venv/bin/activate
  pytest -q
