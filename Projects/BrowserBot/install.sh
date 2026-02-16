#!/bin/bash
# BrowserBot install script
# Usage: bash install.sh

python3 -m venv .browserBot
source .browserBot/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --extra-index-url https://test.pypi.org/simple/

echo "BrowserBot virtual environment is ready. To activate later:"
echo "  source .browserBot/bin/activate"
