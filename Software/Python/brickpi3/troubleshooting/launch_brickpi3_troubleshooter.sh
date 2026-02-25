#!/bin/bash
# BrickPi3 Troubleshooter Launcher
# This script is copied to $HOME by install_trixie.sh, which patches VENV_DIR below.

# Virtual environment to use — patched by install_trixie.sh at install time
VENV_DIR="@@VENV_DIR@@"

# Activate the venv if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "$VENV_DIR/bin/activate" ]; then
        # shellcheck disable=SC1090
        source "$VENV_DIR/bin/activate" || { echo "[ERROR] Failed to activate virtual environment at $VENV_DIR"; exit 1; }
        export VENV_INFO="Activated virtual environment: $VENV_DIR"
        echo "[INFO] $VENV_INFO"
    else
        echo "[ERROR] Virtual environment activate script not found at $VENV_DIR/bin/activate"
        exit 1
    fi
else
    export VENV_INFO="Using already-active virtual environment: $VIRTUAL_ENV"
    echo "[INFO] $VENV_INFO"
fi

# Locate troubleshooter_gui.py via the installed brickpi3 package
TROUBLESHOOTER_GUI="$(python3 -c "import brickpi3, os; print(os.path.join(os.path.dirname(brickpi3.__file__), 'troubleshooting', 'troubleshooter_gui.py'))")"

if [ ! -f "$TROUBLESHOOTER_GUI" ]; then
    echo "[ERROR] troubleshooter_gui.py not found via brickpi3 package (looked at: $TROUBLESHOOTER_GUI)"
    exit 1
fi

echo "[INFO] Launching: $TROUBLESHOOTER_GUI"

# Verify a display is available before launching the GUI
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "[ERROR] No display found (\$DISPLAY and \$WAYLAND_DISPLAY are unset)."
    echo "        Run this from the desktop or use 'ssh -X' for X11 forwarding."
    exit 1
fi

python3 "$TROUBLESHOOTER_GUI"
