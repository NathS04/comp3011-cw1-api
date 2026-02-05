#!/bin/bash
# scripts/smoke_test.sh - Quick validation for deployment

echo "🔥 Running Smoke Test..."

BASE_URL="http://localhost:8000"
if [ ! -z "$1" ]; then
  BASE_URL="$1"
fi

echo "Targeting: $BASE_URL"

# 1. Health
echo "Checking /health..."
curl -s -f "$BASE_URL/health" || { echo "❌ Health check failed"; exit 1; }
echo "✅ Health OK"

# 2. Docs
echo "Checking /docs..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$CODE" != "200" ]; then
  echo "❌ Docs failed with $CODE"
  exit 1
fi
echo "✅ Docs OK"

# 3. Analytics (Public)
echo "Checking analytics..."
curl -s -f "$BASE_URL/analytics/events/seasonality" > /dev/null || { echo "❌ Analytics failed"; exit 1; }
echo "✅ Analytics OK"

echo "✅ Smoke Test Complete. Ready for Oral Demo."
