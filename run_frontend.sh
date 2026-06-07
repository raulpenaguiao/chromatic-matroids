#!/usr/bin/env bash
set -euo pipefail

VENV=".venv"
PORT=5001

# --- Setup ---
if [ ! -d "$VENV" ]; then
    echo "[run_frontend.sh] Creating virtual environment..."
    python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

echo "[run_frontend.sh] Installing dependencies..."
pip install -e package --quiet
pip install pytest numpy flask gunicorn --quiet

# --- Unit tests ---
echo ""
echo "========================================"
echo "  Running unit tests"
echo "========================================"
pytest package/tests/ -v
echo ""

# --- Launch frontend ---
echo "========================================"
echo "  Starting frontend on port $PORT"
echo "  http://localhost:$PORT/chromatic-matroids/"
echo "========================================"
gunicorn \
    --bind "0.0.0.0:$PORT" \
    --workers 1 \
    "frontend.app:create_app()"
