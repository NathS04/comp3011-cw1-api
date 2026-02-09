#!/bin/bash
set -e

echo "🧹 Cleaning repository for release..."

# Define forbidden items
ITEMS_TO_REMOVE=(
    ".venv"
    "venv"
    "node_modules"
    "__pycache__"
    ".pytest_cache"
    ".env"
    "*.db"
    "test.db"
    "app.db"
    "mdpdf.log"
    "comp3011-cw1-api_submission.zip"
    "checkthis.zip"
    "CHECK THIS.zip"
    ".DS_Store"
    "brief.txt"
)

for item in "${ITEMS_TO_REMOVE[@]}"; do
    find . -name "$item" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "$item" -type f -exec rm -f {} + 2>/dev/null || true
    echo "Removed: $item"
done

# Remove any other zip files to be safe
rm -f *.zip

echo "✨ Repository clean."
