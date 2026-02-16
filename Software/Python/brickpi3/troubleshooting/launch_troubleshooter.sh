#!/bin/bash
# BrickPi3 Troubleshooter Launcher
# This script checks for a virtual environment in the BrickPi3 folder, then at the user level, activates it, and launches the troubleshooter GUI.

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Find the BrickPi3 root directory (4 levels up)
BRICKPI3_DIR="$(dirname $(dirname $(dirname $(dirname "$SCRIPT_DIR"))))"
echo "[INFO] BrickPi3 root directory: $BRICKPI3_DIR"

# Virtual environment locations
VENV1="$BRICKPI3_DIR/.venv"
VENV2="$HOME/.venv"

# Function to activate venv and run troubleshooter
run_troubleshooter() {
    source "$1/bin/activate"
    VENV_INFO="Activated virtual environment: $1"
    export VENV_INFO
    echo "[INFO] $VENV_INFO"
    python "$SCRIPT_DIR/troubleshooter_gui.py"
}

if [ -d "$VENV1" ]; then
    run_troubleshooter "$VENV1"
elif [ -d "$VENV2" ]; then
    run_troubleshooter "$VENV2"
else
    echo "No virtual environment found in $VENV1 or $VENV2."
    exit 1
fi
