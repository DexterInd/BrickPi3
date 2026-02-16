# BrickPi3 Trixie Installation

You need internet access for the following step(s).

## Cloning the Repository (Recommended)

To install the BrickPi3 Trixie branch, first clone the repository and run the install script:

1. Open a terminal and run:
   ```bash
   git clone -b trixie https://github.com/DexterInd/BrickPi3.git
   cd BrickPi3/Install
   ```
2. Source the install script:
   ```bash
   source install_trixie.sh
   ```
   - By default, this installs all required software and GUI troubleshooting tools.
   - To install only hardware/driver support (no GUI tools):
     ```bash
     source install_trixie.sh hardware=only
     ```

## Command Options

- `hardware=only` — Only install hardware/driver support, skip GUI troubleshooting tools.
- `user` — Use a user-level Python virtual environment (default is project-level).

## What Gets Installed
- Python virtual environment (if not already active)
- Latest BrickPi3 software from TestPyPI
- (Default) GUI troubleshooting tools for diagnostics and support

## Minimal Installation

If you only want the absolute minimum to get going with the BrickPi3 (no GUI tools):
```bash
source install_trixie.sh hardware=only
```

## Updating

To update your BrickPi3 Trixie installation, simply re-source the install command. Dependencies and the Python package will be updated as needed.

---

For legacy installation instructions or more options, see the original README or the update_brickpi3.sh script.

