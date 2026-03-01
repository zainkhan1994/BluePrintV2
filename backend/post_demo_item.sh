#!/usr/bin/env bash
set -euo pipefail

# Helper script to POST a demo item to the backend API at http://localhost:8100/items
# Usage:
#   chmod +x backend/post_demo_item.sh
#   ./backend/post_demo_item.sh

curl -sS -X POST "http://localhost:8100/items" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "source": "notes",
  "source_ref": "demo-tax-001",
  "title": "IRS payment confirmation",
  "description": "Tax receipt",
  "content": "IRS filing receipt for 2025 and W2 submission completed.",
  "taxonomy_path": "Personal/Important_Documents",
  "idempotency_key": "demo-tax-001"
}
JSON

echo "\nRequest complete."
