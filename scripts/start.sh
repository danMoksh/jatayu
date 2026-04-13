#!/usr/bin/env bash
set -e

echo "Starting Jatayu Mission Control Services..."

# Launch Backend
(
  cd gcs/backend
  source venv/bin/activate 2>/dev/null || true
  python3 run.py
) &
BACKEND_PID=$!

# Launch Frontend
(
  cd gcs/frontend
  npm run dev
) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM

wait
