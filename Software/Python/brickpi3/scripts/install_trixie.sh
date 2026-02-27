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
    # Place venv at the BrickPi3 repo root (four levels up from scripts/)
    VENV_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/.venv"
else
    VENV_DIR="$HOME/.venv/brickpi3"
fi

if [ -z "$VIRTUAL_ENV" ]; then
	if [ -f "$VENV_DIR/bin/activate" ]; then
		echo "No Python virtual environment detected, but $VENV_DIR exists. Activating it..."
		# shellcheck disable=SC1090
		source "$VENV_DIR/bin/activate"
		echo "Activated existing virtual environment at $VENV_DIR."
	elif [ -f "$HOME/.venv/bin/activate" ]; then
		# Also check the common $HOME/.venv location (user may have created their own venv there)
		echo "No Python virtual environment detected, but $HOME/.venv exists. Activating it..."
		# shellcheck disable=SC1090
		source "$HOME/.venv/bin/activate"
		echo "Activated existing virtual environment at $HOME/.venv."
		VENV_DIR="$HOME/.venv"
	else
		echo "No Python virtual environment detected. Creating one with --system-site-packages at $VENV_DIR..."
		python3 -m venv --system-site-packages "$VENV_DIR"
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

# Enable SPI, I2C and VNC interfaces.
# We edit /boot/firmware/config.txt directly for SPI and I2C rather than
# using 'raspi-config nonint do_spi/do_i2c', which rewrites the entire file
# on Trixie and strips essential settings like camera_auto_detect=1.
CONFIG=/boot/firmware/config.txt

echo "Checking SPI interface..."
if grep -qE "^dtparam=spi=on" "$CONFIG"; then
    echo "SPI is already enabled — skipping."
else
    echo "dtparam=spi=on" | sudo tee -a "$CONFIG" > /dev/null
    echo "SPI enabled."
fi

echo "Checking I2C interface..."
if grep -qE "^dtparam=i2c_arm=on" "$CONFIG"; then
    echo "I2C is already enabled — skipping."
else
    echo "dtparam=i2c_arm=on" | sudo tee -a "$CONFIG" > /dev/null
    echo "I2C enabled."
fi

if grep -qi "Lite" /etc/os-release 2>/dev/null; then
    echo "Raspberry Pi OS Lite detected — skipping VNC (no desktop environment)."
else
    echo "Checking VNC interface..."
    if sudo raspi-config nonint get_vnc | grep -q "^0$"; then
        echo "VNC is already enabled — skipping."
    elif sudo raspi-config nonint do_vnc 0; then
        echo "VNC enabled."
    else
        echo "Warning: Failed to enable VNC. You may need to enable it manually in raspi-config."
    fi
fi

# The brickpi3 installation command has been moved here

if python3 -c "import brickpi3" 2>/dev/null; then
    echo "brickpi3 is already installed — skipping pip install."
else
    echo "Installing brickpi3 from PyPI..."
    if ! python3 -m pip install --upgrade brickpi3; then
        echo "Failed to install brickpi3 from PyPI."
        exit 1
    fi
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
        # Use the actual active venv path if one was already active, otherwise the default
        EFFECTIVE_VENV="${VIRTUAL_ENV:-$VENV_DIR}"
        sed -i "s|@@VENV_DIR@@|$EFFECTIVE_VENV|" "$LAUNCH_SCRIPT_COPY"
        chmod +x "$LAUNCH_SCRIPT_COPY"
    else
        echo "Troubleshooter launch script not found at $LAUNCH_SCRIPT"
    fi

    if [ -f "$DESKTOP_FILE" ]; then
        echo "Copying and patching Troubleshooter desktop file to Desktop..."
        TMP_PATCHED_DESKTOP="/tmp/BrickPi3_Troubleshooter.desktop"
        cp "$DESKTOP_FILE" "$TMP_PATCHED_DESKTOP"
        LAUNCH_PATH="$HOME/launch_brickpi3_troubleshooter.sh"
        sed -i "s|^Exec=.*$|Exec=/bin/bash $LAUNCH_PATH|" "$TMP_PATCHED_DESKTOP"

        # Patch the Icon line to use the absolute path to BrickPi3.png in the BrickPi3 root
        BRICKPI3_ROOT="$SCRIPT_DIR/.."
        ICON_PATH="$BRICKPI3_ROOT/troubleshooting/BrickPi3.png"
        sed -i "s|^Icon=.*$|Icon=$ICON_PATH|" "$TMP_PATCHED_DESKTOP"

        mv "$TMP_PATCHED_DESKTOP" "$DESKTOP_TARGET"
        chmod +x "$DESKTOP_TARGET"
        # Mark as trusted so modern Raspberry Pi OS desktop environments will execute it
        gio set "$DESKTOP_TARGET" "metadata::trusted" true 2>/dev/null || true
    else
        echo "Troubleshooter desktop file not found at $DESKTOP_FILE"
    fi
else
    echo "Skipping GUI tools installation (hardware=only mode)"
fi

echo "Installation for $BRANCH branch complete!"
