#!/usr/bin/env bash
# ==============================================================================
# Jatayu GCS - YOLO Model Weights Downloader
# Fetches base YOLOv8 nano and pose detection weights for edge AI inference
# ==============================================================================

set -e

WEIGHTS_DIR="$(dirname "$0")/../gcs/backend"
cd "$WEIGHTS_DIR"

echo "Checking YOLOv8 model weights in $WEIGHTS_DIR..."

# Ultralytics downloads automatically on first run, but this script allows pre-caching:
python3 -c "
from ultralytics import YOLO
import os

print('Pre-loading yolov8n.pt...')
YOLO('yolov8n.pt')
print('Pre-loading yolov8n-pose.pt...')
YOLO('yolov8n-pose.pt')
print('Model weights verified successfully.')
" 2>/dev/null || echo "Ultralytics not yet installed in active environment. Run scripts/setup.sh first."
