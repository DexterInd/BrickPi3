# Check if the script is being sourced or executed
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
	echo "Warning: This script is not being sourced. Any virtual environment activation will not persist in the shell after the script ends."
    echo "To activate the virtual environment in your current shell, run: source install_trixie.sh"
    echo "or activate the virtual environment manually: source .venv/bin/activate upon completion."
	read -n 1 -s -r -p "Press SPACE to continue..." key
    echo
fi

# install_trixie.sh - Custom install script for the 'trixie' branch
# Usage: source install_trixie.sh


set -e

# Check for Python virtual environment
# Usage: bash install_trixie.sh [local|user]

# Default: user-level venv (~/.venv), unless 'local' is specified
if [ "$1" = "local" ]; then
    # Place venv in Software/Python/brickpi3 (one level up from scripts/)
    VENV_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.venv"
else
    VENV_DIR="$HOME/.venv/brickpi3"
fi

if [ -z "$VIRTUAL_ENV" ]; then
	if [ -d "$VENV_DIR" ]; then
		echo "No Python virtual environment detected, but $VENV_DIR exists. Activating it..."
		# shellcheck disable=SC1090
		source "$VENV_DIR/bin/activate"
		echo "Activated existing virtual environment at $VENV_DIR."
	else
		echo "No Python virtual environment detected. Creating one at $VENV_DIR..."
		python3 -m venv "$VENV_DIR"
		# shellcheck disable=SC1090
		source "$VENV_DIR/bin/activate"
		echo "Virtual environment created and activated at $VENV_DIR."
	fi
else
	echo "Python virtual environment detected at $VIRTUAL_ENV."
fi

# Print info
BRANCH="trixie"
echo "Starting installation for BrickPi3 ($BRANCH branch)"

# Enable SPI, I2C and VNC interfaces via raspi-config
echo "Enabling SPI interface..."
if sudo raspi-config nonint do_spi 0; then
    echo "SPI enabled."
else
    echo "Warning: Failed to enable SPI. You may need to enable it manually in raspi-config."
fi

echo "Enabling I2C interface..."
if sudo raspi-config nonint do_i2c 0; then
    echo "I2C enabled."
else
    echo "Warning: Failed to enable I2C. You may need to enable it manually in raspi-config."
fi

if grep -qi "Lite" /etc/os-release 2>/dev/null; then
    echo "Raspberry Pi OS Lite detected — skipping VNC (no desktop environment)."
else
    echo "Enabling VNC interface..."
    if sudo raspi-config nonint do_vnc 0; then
        echo "VNC enabled."
    else
        echo "Warning: Failed to enable VNC. You may need to enable it manually in raspi-config."
    fi
fi

# The brickpi3 installation command has been moved here

echo "Installing brickpi3 from PyPI..."
if ! python3 -m pip install --upgrade brickpi3; then
	echo "Failed to install brickpi3 from PyPI."
	exit 1
fi

echo "Testing brickpi3 installation..."
if ! python3 -c "import brickpi3; print('brickpi3 import successful, software driver version:', getattr(brickpi3, '__version__', 'unknown'))"; then
	echo "brickpi3 import failed!"
	exit 1
fi

# Check for hardware=only parameter
INSTALL_GUI=1
for arg in "$@"; do
    if [ "$arg" = "hardware=only" ]; then
        INSTALL_GUI=0
    fi
done

# After brickpi3 installation and test
if [ "$INSTALL_GUI" -eq 1 ]; then
    echo "Installing GUI tools (trixie_setup_gui.sh)..."
    SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$SCRIPT_DIR/trixie_setup_gui.sh"

    # Desktop integration for Troubleshooter
    SRC_DIR="$SCRIPT_DIR/../troubleshooting"
    DESKTOP_FILE="$SRC_DIR/BrickPi3_Troubleshooter.desktop"
    LAUNCH_SCRIPT="$SRC_DIR/launch_brickpi3_troubleshooter.sh"
    DESKTOP_TARGET="$HOME/Desktop/BrickPi3_Troubleshooter.desktop"


    if [ -f "$LAUNCH_SCRIPT" ]; then
        echo "Copying launch_brickpi3_troubleshooter.sh to $HOME..."
        LAUNCH_SCRIPT_COPY="$HOME/launch_brickpi3_troubleshooter.sh"
        cp "$LAUNCH_SCRIPT" "$LAUNCH_SCRIPT_COPY"
        # Patch the placeholder with the actual venv path used by this install
        sed -i "s|@@VENV_DIR@@|$VENV_DIR|" "$LAUNCH_SCRIPT_COPY"
        chmod +x "$LAUNCH_SCRIPT_COPY"
    else
        echo "Troubleshooter launch script not found at $LAUNCH_SCRIPT"
    fi

    if [ -f "$DESKTOP_FILE" ]; then
        echo "Copying and patching Troubleshooter desktop file to Desktop..."
        TMP_PATCHED_DESKTOP="/tmp/BrickPi3_Troubleshooter.desktop"
        cp "$DESKTOP_FILE" "$TMP_PATCHED_DESKTOP"
        LAUNCH_PATH="$HOME/launch_brickpi3_troubleshooter.sh"
        # Escape spaces for .desktop Exec line
        LAUNCH_PATH_ESCAPED="${LAUNCH_PATH// /\\ }"
        sed -i "s|^Exec=.*$|Exec=\"$LAUNCH_PATH_ESCAPED\"|" "$TMP_PATCHED_DESKTOP"

        # Patch the Icon line to use the absolute path to BrickPi3.png in the BrickPi3 root
        BRICKPI3_ROOT="$SCRIPT_DIR/.."
        ICON_PATH="$BRICKPI3_ROOT/troubleshooting/BrickPi3.png"
        sed -i "s|^Icon=.*$|Icon=$ICON_PATH|" "$TMP_PATCHED_DESKTOP"

        mv "$TMP_PATCHED_DESKTOP" "$DESKTOP_TARGET"
    else
        echo "Troubleshooter desktop file not found at $DESKTOP_FILE"
    fi
else
    echo "Skipping GUI tools installation (hardware=only mode)"
fi

echo "Installation for $BRANCH branch complete!"
