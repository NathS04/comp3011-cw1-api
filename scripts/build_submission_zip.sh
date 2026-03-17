#!/bin/bash
set -e

echo "Building submission zip..."

ZIP_NAME="comp3011-cw1-api_submission_FINAL.zip"
rm -f "$ZIP_NAME"

# Clean caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

zip -r "$ZIP_NAME" . \
    -x ".git/*" \
    -x ".gitignore" \
    -x ".venv/*" \
    -x "venv/*" \
    -x "venv_test/*" \
    -x "venv*/*" \
    -x "node_modules/*" \
    -x "*/__pycache__/*" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x ".pytest_cache/*" \
    -x "*/.pytest_cache/*" \
    -x ".mypy_cache/*" \
    -x "*/.mypy_cache/*" \
    -x ".ruff_cache/*" \
    -x "*/.ruff_cache/*" \
    -x ".coverage" \
    -x "coverage.xml" \
    -x "htmlcov/*" \
    -x ".env" \
    -x ".env.example" \
    -x "*.db" \
    -x "test.db" \
    -x "app.db" \
    -x "mdpdf.log" \
    -x "*.zip" \
    -x ".DS_Store" \
    -x "*/.DS_Store" \
    -x "brief.txt" \
    -x ".gemini/*" \
    -x ".antigravity/*" \
    -x ".antigravityignore" \
    -x ".agent/*" \
    -x "verify/*" \
    -x "package.json" \
    -x "package-lock.json" \
    -x "COMP3011_Coursework1_Brief*.pdf" \
    -x "implementation_plan.md" \
    -x "task.md" \
    -x "walkthrough.md" \
    -x "*.html" \
    -x "docs/*.html" \
    -x "docs/appendix_genai_logs.md" \
    -x "scripts/clean_release.sh"

echo ""
echo "Created $ZIP_NAME"
ls -lh "$ZIP_NAME"

echo ""
echo "--- Forbidden files (should be EMPTY) ---"
zipinfo -1 "$ZIP_NAME" | grep -E "(\.git/|venv/|node_modules/|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.coverage$|coverage\.xml$|htmlcov/|\.env$|\.db$|\.html$|package\.json|package-lock|Brief|implementation_plan|task\.md|walkthrough\.md|appendix_genai)" || echo "CLEAN: No forbidden files found"

echo ""
echo "--- Key files (should be present) ---"
zipinfo -1 "$ZIP_NAME" | grep -E "(README\.md|TECHNICAL_REPORT\.(md|pdf)|VERIFICATION|requirements\.txt|render\.yaml|app/main|tests/|docs/API_DOC|docs/GENAI|docs/PRESENTATION|docs/DATASET|scripts/(import|quality|verify|build))" | head -25
