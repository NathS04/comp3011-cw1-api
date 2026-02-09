#!/bin/bash
set -e

# 1. Clean first
./scripts/clean_release.sh

echo "📦 Building submission zip..."

ZIP_NAME="comp3011-cw1-api_submission_FINAL.zip"

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
    -x ".env" \
    -x ".env.example" \
    -x "*.db" \
    -x "test.db" \
    -x "app.db" \
    -x "mdpdf.log" \
    -x "*.zip" \
    -x ".DS_Store" \
    -x "brief.txt" \
    -x ".gemini/*" \
    -x ".antigravity/*" \
    -x "scripts/clean_release.sh" \
    -x "scripts/build_submission_zip.sh" \
    -x "verify/*"

echo "✅ Created $ZIP_NAME"
ls -lh "$ZIP_NAME"
