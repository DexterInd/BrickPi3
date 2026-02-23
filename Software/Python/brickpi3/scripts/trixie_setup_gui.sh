#!/bin/bash

# Setup script for BrickPi3 GUI tools
# This script installs wxPython and creates necessary symlinks for virtual environments

set -e

echo "Setting up BrickPi3 GUI tools..."

# Check if wxPython is already installed
if dpkg -l | grep -q python3-wxgtk4.0; then
    echo "python3-wxgtk4.0 is already installed"
else
    # Install wxPython system package
    echo "Installing python3-wxgtk4.0..."
    sudo apt update
    sudo apt install -y python3-wxgtk4.0
fi

# If running in a virtual environment, create symlink
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment detected: $VIRTUAL_ENV"

    # Find the correct site-packages directory
    SITE_PACKAGES=$(find "$VIRTUAL_ENV/lib" -type d -name "site-packages" | head -1)

    if [ -n "$SITE_PACKAGES" ]; then
        echo "Creating symlink to system wxPython..."

        # Remove existing symlink if it exists
        if [ -L "$SITE_PACKAGES/wx" ]; then
            rm "$SITE_PACKAGES/wx"
        fi

        # Create symlink to system wx package
        ln -sf /usr/lib/python3/dist-packages/wx "$SITE_PACKAGES/wx"

        echo "Symlink created successfully"

        # Test the installation
        if "$VIRTUAL_ENV/bin/python" -c "import wx; print('wxPython version:', wx.version())" 2>/dev/null; then
            echo "✓ wxPython is working correctly in the virtual environment"
        else
            echo "✗ Warning: wxPython import failed. You may need to check the installation."
        fi
    else
        echo "✗ Could not find site-packages directory in virtual environment"
        exit 1
    fi
else
    echo "No virtual environment detected. wxPython is installed system-wide."

    # Test system installation
    if python3 -c "import wx; print('wxPython version:', wx.version())" 2>/dev/null; then
        echo "✓ wxPython is working correctly"
    else
        echo "✗ Warning: wxPython import failed. You may need to reinstall."
    fi
fi

echo ""
echo "Setup complete! You can now run GUI tools like:"
echo "  python brickpi3/examples/troubleshoot.py"
