#!/bin/bash
set -e

echo "============================================"
echo "  Arithmetic Math Solver - Railway Startup  "
echo "============================================"

# Set defaults
export PORT="${PORT:-3000}"
export ROOT_URL="${ROOT_URL:-http://localhost:$PORT}"
export PYTHON_SERVICE_URL="${PYTHON_SERVICE_URL:-http://localhost:5000}"
export MONGO_URL="${MONGO_URL:-mongodb://localhost:27017/arithmetic}"

echo "[startup] PORT=$PORT"
echo "[startup] ROOT_URL=$ROOT_URL"
echo "[startup] PYTHON_SERVICE_URL=$PYTHON_SERVICE_URL"

# Start Python service in background
echo "[startup] Starting Python math service..."
bash scripts/start-python.sh &
PYTHON_PID=$!
echo "[startup] Python service PID: $PYTHON_PID"

# Wait for Python service to be ready
echo "[startup] Waiting for Python service..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf "$PYTHON_SERVICE_URL/health" > /dev/null 2>&1; then
        echo "[startup] Python service is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "[startup] Waiting for Python service... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "[startup] WARNING: Python service not responding, continuing anyway..."
fi

# Start Meteor
echo "[startup] Starting Meteor application..."
exec meteor run --port "$PORT" --production
