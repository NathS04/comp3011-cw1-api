#!/bin/bash
set -e

echo "=== Ruff ==="
ruff check .

echo "=== Mypy ==="
mypy app scripts/import_dataset.py scripts/make_admin.py scripts/clean_db.py

echo "=== Bandit ==="
bandit -r app scripts -q

echo "=== Tests ==="
pytest -q

echo "=== Coverage ==="
pytest --cov=app --cov-report=term-missing -q

echo ""
echo "All quality gates passed."
