
#!/bin/bash
set -e

echo "Running Ruff..."
ruff check .

echo "Running Mypy..."
mypy app

echo "Running Bandit..."
bandit -r app -q

echo "Running Helpers..."
if command -v pip-audit &> /dev/null; then
    echo "Running pip-audit..."
    pip-audit
fi

echo "Running Tests..."
pytest -q
