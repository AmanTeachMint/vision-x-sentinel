#!/bin/bash
# Fix "operator torchvision::nms does not exist" by using a clean venv (no system/user packages).
# Run on VM: cd ~/vision-x-sentinel/backend && bash scripts/fix_torch_venv.sh

set -e
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BACKEND_DIR"
echo "=== Backend directory: $BACKEND_DIR ==="

# Use system python3 to create venv (do NOT activate old venv yet)
SYS_PYTHON=$(which python3)
echo "Using system Python: $SYS_PYTHON"

# Remove old venv so we start clean (no .local inheritance)
if [ -d "venv" ]; then
  echo "Removing old venv..."
  rm -rf venv
fi

# Create new venv (default: no system-site-packages, so we don't use .local)
echo "Creating new venv..."
"$SYS_PYTHON" -m venv venv
"$BACKEND_DIR/venv/bin/python3" -m pip install --upgrade pip

# Use venv's python and pip explicitly (no PATH ambiguity)
VENV_PYTHON="$BACKEND_DIR/venv/bin/python3"
VENV_PIP="$BACKEND_DIR/venv/bin/pip"

echo "Installing torch + torchvision (CPU) in venv..."
"$VENV_PIP" install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "Installing requirements in venv..."
"$VENV_PIP" install -r requirements.txt

echo "Verifying YOLO import (must use venv python)..."
"$VENV_PYTHON" -c "from ultralytics import YOLO; print('OK')"

echo ""
echo "=== Done ==="
echo "Start backend with: $VENV_PYTHON run.py"
echo "Or: cd $BACKEND_DIR && ./venv/bin/python3 run.py"
echo "PM2: pm2 start run.py --name backend --interpreter $BACKEND_DIR/venv/bin/python3 --cwd $BACKEND_DIR"
