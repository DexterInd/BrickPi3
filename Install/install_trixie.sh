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
# Usage: bash install_trixie.sh [user]

if [ "$1" = "user" ]; then
	VENV_DIR="$HOME/.venv"
else
	VENV_DIR="$(pwd)/.venv"
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

# The brickpi3 installation command has been moved here

echo "Installing brickpi3 from TestPyPI..."
if ! python3 -m pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple brickpi3; then
	echo "Failed to install brickpi3 from TestPyPI."
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
    bash "$(dirname "$0")/trixie_setup_gui.sh"

    # Desktop integration for Troubleshooter
    # Determine source folder for .desktop and launch script
    SRC_DIR="$(dirname "$0")/../Software/Python/brickpi3/troubleshooting"
    DESKTOP_FILE="$SRC_DIR/BrickPi3_Troubleshooter.desktop"
    LAUNCH_SCRIPT="$SRC_DIR/launch_troubleshooter.sh"
    DESKTOP_TARGET="$HOME/Desktop/BrickPi3_Troubleshooter.desktop"

    if [ -f "$DESKTOP_FILE" ]; then
        echo "Linking Troubleshooter desktop file to Desktop..."
        ln -sf "$DESKTOP_FILE" "$DESKTOP_TARGET"
    else
        echo "Troubleshooter desktop file not found at $DESKTOP_FILE"
    fi

    if [ -f "$LAUNCH_SCRIPT" ]; then
        echo "Setting execution flag on launch_troubleshooter.sh..."
        chmod +x "$LAUNCH_SCRIPT"
    else
        echo "Troubleshooter launch script not found at $LAUNCH_SCRIPT"
    fi
else
    echo "Skipping GUI tools installation (hardware=only mode)"
fi

echo "Installation for $BRANCH branch complete!"
