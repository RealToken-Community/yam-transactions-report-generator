#!/usr/bin/env bash
set -euo pipefail

PORT="${API_PORT_INTERNAL:-5000}"
WORKERS=1
THREADS=2

echo "Starting API on port ${PORT} with ${WORKERS} worker(s) and ${THREADS} thread(s)..."

exec gunicorn \
  --workers "${WORKERS}" \
  --threads "${THREADS}" \
  --bind "0.0.0.0:${PORT}" \
  "API.core.app:create_app()"
