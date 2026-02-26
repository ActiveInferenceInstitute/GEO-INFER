# Installation Issues

This guide covers common installation problems for the GEO-INFER framework, including Python version requirements, system dependencies, and platform-specific fixes.

## Prerequisites

### Python Version

GEO-INFER requires Python 3.9 or later. Check your version:

```bash
python3 --version
```

If you need to install a specific Python version:

```bash
# macOS (Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-dev

# Windows (winget)
winget install Python.Python.3.11
```

### uv Package Manager

GEO-INFER uses `uv` as its package manager. Install it first:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

**Common uv issues:**

| Issue | Fix |
|-------|-----|
| `command not found: uv` | Add `~/.cargo/bin` to PATH, or restart your shell |
| `uv pip` fails silently | Ensure you are in a virtual environment or use `--system` |
| Old version of uv | `uv self update` |

## Installing GEO-INFER Modules

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER

# Create a virtual environment
uv venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install core modules (editable mode)
uv pip install -e ./GEO-INFER-MATH
uv pip install -e ./GEO-INFER-SPACE
uv pip install -e ./GEO-INFER-ACT
```

### Installing Multiple Modules

```bash
# Install a working set of modules
uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE ./GEO-INFER-ACT ./GEO-INFER-BAYES ./GEO-INFER-TIME

# Install with optional development extras
uv pip install -e "./GEO-INFER-AI[dev,docs]"
```

### Editable Install Issues

**Problem:** `uv pip install -e ./GEO-INFER-SPACE` fails with "No pyproject.toml found".

**Fix:** Ensure you are running the command from the repository root, not from inside the module directory.

```bash
# Wrong (from inside the module)
cd GEO-INFER-SPACE
uv pip install -e .  # may fail if dependencies reference sibling modules

# Correct (from repo root)
cd /path/to/GEO-INFER
uv pip install -e ./GEO-INFER-SPACE
```

**Problem:** Editable install succeeds but imports fail.

**Fix:** Check that the `src` layout is correct. GEO-INFER uses `src/geo_infer_module/` layout:

```bash
# Verify the package is findable
python -c "import geo_infer_space; print(geo_infer_space.__file__)"
```

If this prints `None` or a path outside your repo, the editable install may have linked to a stale build. Reinstall:

```bash
uv pip install --force-reinstall -e ./GEO-INFER-SPACE
```

## GDAL System Dependency

Several GEO-INFER modules depend on GDAL through `rasterio`, `fiona`, or `geopandas`. GDAL requires system-level libraries.

### macOS

```bash
# Install GDAL via Homebrew
brew install gdal

# Verify
gdal-config --version

# Install Python bindings matching system version
uv pip install GDAL==$(gdal-config --version)
```

**Common macOS issues:**

| Error | Fix |
|-------|-----|
| `gdal-config: command not found` | `brew install gdal` |
| `ld: library not found for -lgdal` | `export CFLAGS="-I$(brew --prefix gdal)/include" LDFLAGS="-L$(brew --prefix gdal)/lib"` |
| Architecture mismatch (arm64 vs x86_64) | Ensure Homebrew and Python are both arm64 or both x86_64 |

### Linux (Ubuntu/Debian)

```bash
# Install GDAL and development headers
sudo apt update
sudo apt install gdal-bin libgdal-dev python3-gdal

# Set environment for pip
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal

uv pip install GDAL==$(gdal-config --version)
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install gdal gdal-devel python3-gdal
```

### Windows

The simplest approach on Windows is to use pre-built wheels:

```bash
# Install from Christoph Gohlke's wheels or conda-forge
uv pip install rasterio fiona geopandas

# If that fails, use conda
conda install -c conda-forge gdal rasterio fiona geopandas
```

## H3 Library Installation

H3 v4 is required. The Python `h3` package includes pre-built wheels for most platforms.

```bash
uv pip install "h3>=4.0.0"

# Verify
python -c "import h3; print(h3.versions())"
```

**If wheels are not available for your platform** (rare), you need the H3 C library:

```bash
# macOS
brew install h3

# Ubuntu
sudo apt install cmake
pip install h3 --no-binary h3  # builds from source
```

**H3 v3 vs v4 check:**

```python
import h3

# This works on v4 only
try:
    h3.latlng_to_cell(37.7749, -122.4194, 7)
    print("H3 v4 installed correctly")
except AttributeError:
    print("ERROR: H3 v3 installed. Upgrade with: uv pip install 'h3>=4.0.0'")
```

## Common pip/uv Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `ResolutionImpossible` | Conflicting version requirements | Check which modules have conflicting deps: `uv pip check` |
| `ERROR: No matching distribution` | Package not available for your Python/OS | Check PyPI for available platforms; consider building from source |
| `subprocess-exited-with-error` during install | C extension build failed | Install system dev libraries (gcc, python3-dev, libffi-dev) |
| `externally-managed-environment` | System Python refuses pip installs | Use a virtual environment: `uv venv .venv && source .venv/bin/activate` |
| `error: legacy-install-failure` | Old setup.py that fails with modern pip | Try `uv pip install --no-build-isolation package` |

## Virtual Environment Conflicts

### Multiple Virtual Environments

If you have multiple environments, ensure you activate the correct one:

```bash
# Check which Python is active
which python
python -c "import sys; print(sys.prefix)"

# List installed GEO-INFER modules
uv pip list | grep geo-infer
```

### Conda + uv Interaction

If you use conda for system dependencies (GDAL) and uv for Python packages:

```bash
# Create conda env with system deps
conda create -n geoinfer python=3.11 gdal rasterio fiona -c conda-forge
conda activate geoinfer

# Install GEO-INFER modules with uv inside the conda env
uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE
```

Do not mix `conda install` and `uv pip install` for the same package. Use conda for C-library dependencies and uv for pure-Python packages.

## Platform-Specific Notes

### macOS (Apple Silicon)

- Use the arm64 Homebrew (`/opt/homebrew/bin/brew`)
- Ensure Python is arm64: `python -c "import platform; print(platform.machine())"`
- Some packages may require Rosetta 2 for x86_64 emulation
- If `numpy` or `scipy` build fails, install via: `uv pip install numpy scipy` (wheels are available for arm64)

### Windows

- Use PowerShell or Windows Terminal, not Command Prompt
- Long path issues: enable long paths in Group Policy or registry
- Use WSL2 for the most compatible experience with geospatial libraries
- Visual Studio Build Tools may be needed for packages without wheels

### Linux

- Install `python3-dev` (or `python3-devel` on Fedora) for C extension compilation
- Install `libspatialindex-dev` for `rtree` / shapely spatial indexing
- Ensure `proj` and `geos` development headers are installed for shapely/pyproj

## Verification After Installation

Run these checks to verify your installation:

```bash
# 1. Check Python version
python --version  # Should be 3.9+

# 2. Check core imports
python -c "
import geo_infer_math; print('MATH OK')
import geo_infer_space; print('SPACE OK')
import geo_infer_act; print('ACT OK')
"

# 3. Check H3 version
python -c "import h3; print(f'H3 v4: {hasattr(h3, \"latlng_to_cell\")}')"

# 4. Check GDAL (if needed)
python -c "from osgeo import gdal; print(f'GDAL {gdal.VersionInfo()}')"

# 5. Run module tests
uv run python -m pytest GEO-INFER-MATH/tests/ -v --tb=short -q
```

## Getting Further Help

If the above steps do not resolve your issue:

1. Search [GitHub Issues](https://github.com/ActiveInferenceInstitute/GEO-INFER/issues)
2. Check [Troubleshooting](troubleshooting.md) for runtime errors
3. File a new issue with your OS, Python version, full error output, and the commands you ran

## See Also

- [Troubleshooting](troubleshooting.md) -- runtime error diagnosis
- [Performance Issues](performance_issues.md) -- slow execution and memory problems
- [FAQ](faq.md) -- frequently asked questions
