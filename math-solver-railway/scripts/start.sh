#!/bin/bash
set -e

echo "Starting Arithmetic Math Solver (Development)..."

# Start Python service in background
bash scripts/start-python.sh &

# Wait briefly for Python to initialize
sleep 3

# Start Meteor in development mode
meteor run --port ${PORT:-3000}
