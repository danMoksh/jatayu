#!/usr/bin/env bash
set -e

echo "=================================================="
echo "  Jatayu VTOL & GCS System Setup"
echo "=================================================="

# 1. Backend Setup
echo "[1/3] Setting up Python Backend..."
cd gcs/backend
python3 -m venv venv || python -m venv venv
source venv/bin/activate || source venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ../..

# 2. Frontend Setup
echo "[2/3] Setting up React Frontend..."
cd gcs/frontend
npm install
npm run build
cd ../..

# 3. Directories verification
echo "[3/3] Initializing local storage directories..."
mkdir -p gcs/backend/recordings gcs/backend/uploads docs/assets

echo "Setup completed successfully!"
