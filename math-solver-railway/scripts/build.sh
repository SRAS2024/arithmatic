#!/bin/bash
set -e

echo "Building Arithmetic Math Solver..."

# Install Node dependencies
echo "[build] Installing Node.js dependencies..."
meteor npm install

# Setup Python environment
echo "[build] Setting up Python environment..."
cd python
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

# Build Meteor
echo "[build] Building Meteor application..."
meteor build --directory ../build --server-only

echo "[build] Build complete!"
