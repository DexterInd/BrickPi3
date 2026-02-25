#!/bin/bash

# Setup script for BrickPi3 GUI tools
# The BrickPi3 Troubleshooter uses tkinter, which is provided by the system package python3-tk.

set -e

echo "Setting up BrickPi3 GUI tools..."

# Check if python3-tk is already installed
if dpkg -l | grep -q python3-tk; then
    echo "python3-tk is already installed"
else
    echo "Installing python3-tk..."
    sudo apt update
    sudo apt install -y python3-tk
fi

# Verify tkinter works in the active Python environment
if python3 -c "import tkinter" 2>/dev/null; then
    echo "✓ tkinter is working correctly"
else
    echo "✗ Warning: tkinter import failed. You may need to reinstall python3-tk."
fi

echo ""
echo "Setup complete!"
