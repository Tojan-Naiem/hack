#!/usr/bin/env bash
# Serve project root (frontend files) on http://localhost:5500
# Usage: ./scripts/serve_frontend.sh

PORT=5500
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Serving frontend from $ROOT_DIR on http://localhost:$PORT"
cd "$ROOT_DIR" || exit 1
# Use python's http.server (works with python3)
python3 -m http.server "$PORT" --bind 127.0.0.1
