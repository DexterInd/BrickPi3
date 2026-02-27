#!/usr/bin/env bash
# install_browserbot.sh - Install dependencies for the BrowserBot project
# Usage: bash install_browserbot.sh
#
# Assumes: Python virtual environment and brickpi3 are already installed.
# Installs:
#   - libcamera-apps, python3-libcamera, python3-picamera2  (system packages)
#   - tornado                                               (Python package)

set -e

# ---------------------------------------------------------------------------
# Require a virtual environment
# ---------------------------------------------------------------------------
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: no active Python virtual environment detected."
    echo "Activate one first, e.g.:"
    echo "  source ~/.venv/brickpi3/bin/activate"
    exit 1
fi
echo "Using virtual environment: $VIRTUAL_ENV"

echo "=== BrowserBot Dependency Installer ==="

# ---------------------------------------------------------------------------
# 1. System packages (libcamera + picamera2)
# ---------------------------------------------------------------------------
echo ""
echo "Checking system packages..."
SYS_PKGS=(libcamera-apps python3-libcamera python3-picamera2)
MISSING_SYS=()
for pkg in "${SYS_PKGS[@]}"; do
    if ! dpkg -s "$pkg" &>/dev/null; then
        MISSING_SYS+=("$pkg")
    fi
done

if [ ${#MISSING_SYS[@]} -gt 0 ]; then
    echo "Installing: ${MISSING_SYS[*]}"
    sudo apt-get update -qq
    sudo apt-get install -y "${MISSING_SYS[@]}"
    echo "System packages installed."
else
    echo "System packages already installed — skipping."
fi

# ---------------------------------------------------------------------------
# 2. Python package: tornado
# ---------------------------------------------------------------------------
echo ""
if python3 -c "import tornado" 2>/dev/null; then
    echo "tornado already installed — skipping."
else
    echo "Installing tornado..."
    python3 -m pip install --upgrade tornado
fi

# ---------------------------------------------------------------------------
# 3. Verify camera is visible
# ---------------------------------------------------------------------------
echo ""
echo "Checking camera..."
if command -v rpicam-hello &>/dev/null; then
    if rpicam-hello --list-cameras 2>&1 | grep -q "Available cameras"; then
        echo "Camera detected."
    else
        echo "Warning: no camera detected. Check ribbon cable and run: rpicam-hello --list-cameras"
    fi
else
    echo "Warning: rpicam-hello not found. A reboot may be required."
fi

echo ""
echo "BrowserBot installation complete!"
echo "Run the server with:  python stream_server.py"
