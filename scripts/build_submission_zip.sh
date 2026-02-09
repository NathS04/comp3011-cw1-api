#!/bin/bash
set -e

# 1. Clean first
./scripts/clean_release.sh

echo "📦 Building submission zip..."

ZIP_NAME="comp3011-cw1-api_submission_FINAL.zip"

# Remove any existing zip
rm -f "$ZIP_NAME"

# 2. Create Zip with strict exclusions
zip -r "$ZIP_NAME" . \
    -x ".git/*" \
    -x ".gitignore" \
    -x ".venv/*" \
    -x "venv/*" \
    -x "node_modules/*" \
    -x "*/__pycache__/*" \
    -x "__pycache__/*" \
    -x ".pytest_cache/*" \
    -x "*/.pytest_cache/*" \
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
    -x ".agent/*" \
    -x "scripts/clean_release.sh" \
    -x "scripts/build_submission_zip.sh"

echo ""
echo "✅ Created $ZIP_NAME"
ls -lh "$ZIP_NAME"

echo ""
echo "📋 Contents check:"
echo "--- Forbidden files (should be EMPTY) ---"
zipinfo -1 "$ZIP_NAME" | grep -E "(\.git/|venv/|node_modules/|__pycache__|\.pytest_cache|\.env$|\.db$|\.html$|package\.json|package-lock|Brief|implementation_plan|task\.md|walkthrough\.md|appendix_genai)" || echo "CLEAN: No forbidden files found ✅"

echo ""
echo "--- Key files (should be present) ---"
zipinfo -1 "$ZIP_NAME" | grep -E "(README\.md|TECHNICAL_REPORT\.(md|pdf)|VERIFICATION|requirements\.txt|render\.yaml|app/main|tests/|docs/API_DOC|docs/GENAI|docs/PRESENTATION|docs/DATASET|scripts/import)" | head -20
