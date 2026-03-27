#!/bin/bash
set -e

echo "[python] Starting Python math service..."

PYTHON_DIR="$(dirname "$0")/../python"
VENV_PATH="${PYTHON_VENV_PATH:-$PYTHON_DIR/venv}"
PYTHON_PORT="${PYTHON_PORT:-5000}"

# Activate virtual environment if it exists
if [ -d "$VENV_PATH" ]; then
    echo "[python] Using virtual environment: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
else
    echo "[python] No virtual environment found, using system Python"
fi

# Install dependencies if needed
if [ -f "$PYTHON_DIR/requirements.txt" ]; then
    echo "[python] Checking Python dependencies..."
    pip install -q -r "$PYTHON_DIR/requirements.txt" 2>/dev/null || true
fi

cd "$PYTHON_DIR"

echo "[python] Starting uvicorn on port $PYTHON_PORT..."
exec python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PYTHON_PORT" \
    --log-level info \
    --timeout-keep-alive 30
