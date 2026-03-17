#!/bin/bash
set -e
FAIL=0

fail() { echo "FAIL: $1"; FAIL=1; }
pass() { echo "OK:   $1"; }

echo "=== Submission Verification ==="
echo ""

# Required PDFs
for f in TECHNICAL_REPORT.pdf docs/API_DOCUMENTATION.pdf docs/GENAI_EXPORT_LOGS.pdf; do
    [ -f "$f" ] && pass "$f exists" || fail "$f missing"
done

# Technical report page count (requires python3)
if [ -f TECHNICAL_REPORT.pdf ]; then
    PAGES=$(python3 -c "
import subprocess, re
r = subprocess.run(['mdls', '-name', 'kMDItemNumberOfPages', 'TECHNICAL_REPORT.pdf'], capture_output=True, text=True)
m = re.search(r'(\d+)', r.stdout)
print(m.group(1) if m else 'unknown')
" 2>/dev/null || echo "unknown")
    if [ "$PAGES" != "unknown" ] && [ "$PAGES" -le 5 ] 2>/dev/null; then
        pass "Technical report is $PAGES pages (<= 5)"
    elif [ "$PAGES" != "unknown" ]; then
        fail "Technical report is $PAGES pages (must be <= 5)"
    else
        echo "SKIP: Could not determine PDF page count"
    fi
fi

# Tests
echo ""
echo "--- Running pytest ---"
pytest -q 2>&1 && pass "pytest passes" || fail "pytest failed"

echo ""
echo "--- Running coverage ---"
COVERAGE_OUTPUT=$(pytest --cov=app --cov-report=term -q 2>&1) || {
    echo "$COVERAGE_OUTPUT"
    fail "coverage run failed"
}
echo "$COVERAGE_OUTPUT"
if printf "%s" "$COVERAGE_OUTPUT" | grep -Eq "TOTAL.+ 9[4-9]%|TOTAL.+100%"; then
    pass "coverage meets >= 94%"
else
    fail "coverage below 94%"
fi

# Ruff
echo ""
echo "--- Running ruff ---"
ruff check . 2>&1 && pass "ruff clean" || fail "ruff has errors"

# Mypy
echo ""
echo "--- Running mypy ---"
mypy app scripts/import_dataset.py scripts/make_admin.py scripts/clean_db.py 2>&1 && pass "mypy clean" || fail "mypy has errors"

# Bandit
echo ""
echo "--- Running bandit ---"
bandit -r app scripts -q 2>&1 && pass "bandit clean" || fail "bandit has issues"

# Stale references
echo ""
echo "--- Checking for stale references ---"
if grep -rn "41 passed\|43 passed\|41 tests\|43 tests" README.md TECHNICAL_REPORT.md VERIFICATION_INSTRUCTIONS.md docs/*.md 2>/dev/null; then
    fail "Stale test count references found"
else
    pass "No stale test count references"
fi

if grep -rn "92% coverage\|90% coverage\|91% coverage\|93% coverage" README.md TECHNICAL_REPORT.md VERIFICATION_INSTRUCTIONS.md docs/*.md 2>/dev/null; then
    fail "Stale coverage references found"
else
    pass "No stale coverage references"
fi

if grep -rn "version.*1\.4\.0" README.md TECHNICAL_REPORT.md docs/API_DOCUMENTATION.md 2>/dev/null; then
    fail "Stale version 1.4.0 references found"
else
    pass "No stale version references"
fi

if rg -n "submission\.zip|comp3011-cw1-api_submission\.zip" README.md VERIFICATION_INSTRUCTIONS.md docs/*.md >/dev/null 2>&1; then
    fail "Stale zip name references found"
else
    pass "No stale zip name references"
fi

echo ""
echo "--- Checking docs for standout endpoints ---"
for endpoint in "/events/{id}/provenance" "/admin/imports/quality"; do
    if grep -q "$endpoint" docs/API_DOCUMENTATION.md README.md VERIFICATION_INSTRUCTIONS.md; then
        pass "Docs reference $endpoint"
    else
        fail "Docs missing $endpoint"
    fi
done

# README links
echo ""
echo "--- Checking README links ---"
for target in TECHNICAL_REPORT.pdf docs/API_DOCUMENTATION.pdf docs/GENAI_EXPORT_LOGS.pdf; do
    if grep -q "$target" README.md; then
        pass "README links to $target"
    else
        fail "README missing link to $target"
    fi
done

echo ""
if [ $FAIL -eq 0 ]; then
    echo "=== ALL CHECKS PASSED ==="
else
    echo "=== SOME CHECKS FAILED ==="
    exit 1
fi
