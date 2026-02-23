# BrickPi3 Python Package

Modern Python package for BrickPi3 hardware drivers, configured using `pyproject.toml`.

## Installation

### From PyPI (Recommended)

Once published, install with:

```bash
pip install brickpi3
```

On Raspberry Pi OS, this automatically gets optimized ARM wheels from piwheels.

### From Source

```bash
cd Software/Python
pip install .
```

## Development Installation

For development with editable install:

```bash
cd Software/Python
pip install -e .
```

## Package Structure

```
Software/Python/
├── pyproject.toml    # Modern package configuration (PEP 517/518)
├── MANIFEST.in       # Additional files to include in distribution
├── brickpi3.py       # Main driver module
├── scripts/          # Install scripts
├── troubleshooting/  # Troubleshooting scripts
└── examples/         # Example scripts
```

## Configuration Details

### pyproject.toml

This file contains all package metadata:

- **Project metadata**: name, version, description, authors
- **Dependencies**: `spidev` for SPI communication
- **Python requirements**: >=3.7
- **Classifiers**: Platform, development status, audience
- **URLs**: Homepage, documentation, repository, bug tracker

### Version Management

Version is specified in `pyproject.toml`:

```toml
[project]
version = "4.0.5"
```

Update this for each release before building.

## Building

Build source distribution and wheel:

```bash
cd Software/Python
python -m build
```

This creates:
- `dist/brickpi3-4.0.5.tar.gz` (source distribution)
- `dist/brickpi3-4.0.5-py3-none-any.whl` (wheel)

## Publishing

See [PYPI_PUBLISHING.md](../../PYPI_PUBLISHING.md) for detailed instructions on publishing to PyPI.

## Requirements

- **Python**: 3.7 or higher
- **Platform**: Raspberry Pi OS (Linux only)
- **Hardware**: BrickPi3 board
- **Dependencies**:
  - `spidev` - SPI interface (automatically installed)

## License

MIT License - see [LICENSE.md](../../LICENSE.md)

## Links

- **Homepage**: https://www.dexterindustries.com/BrickPi/
- **Documentation**: https://www.dexterindustries.com/brickpi3-tutorials-documentation/
- **Repository**: https://github.com/DexterInd/BrickPi3
- **PyPI**: https://pypi.org/project/brickpi3/ (once published)
- **PyWheels**: https://www.piwheels.org/project/brickpi3/ (automatic after PyPI)
