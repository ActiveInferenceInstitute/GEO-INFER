# GEO-INFER Installation Guide

This guide covers installing the GEO-INFER framework, its system dependencies,
individual modules, and troubleshooting common issues.

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.9 | 3.11 or 3.12 |
| RAM | 4 GB | 8 GB (16 GB for ML modules) |
| Disk Space | 5 GB | 20 GB (with sample data) |
| OS | Linux, macOS, Windows (WSL2) | Linux (Ubuntu 22.04+), macOS 13+ |

### Supported Platforms

- **Linux**: Ubuntu 20.04+, Debian 11+, RHEL 8+, Fedora 36+
- **macOS**: 12 (Monterey) or later, both Intel and Apple Silicon
- **Windows**: Windows 10/11 with WSL2 (native Windows is not tested)

## Installing uv

GEO-INFER uses `uv` as its package manager. Install it first.

### Option A: Standalone installer (recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your shell or source the profile:

```bash
source ~/.bashrc   # or ~/.zshrc on macOS
```

### Option B: Via pip

```bash
pip install uv
```

### Verify uv Installation

```bash
uv --version
# Output: uv 0.5.x (or later)
```

## Installing the Framework

### Step 1: Clone the Repository

```bash
git clone https://github.com/activeinference/GEO-INFER.git
cd GEO-INFER
```

### Step 2: Create a Virtual Environment

```bash
uv venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows WSL2
```

### Step 3: Install Core Modules

Install the foundational modules that most other modules depend on:

```bash
uv pip install -e ./GEO-INFER-MATH
uv pip install -e ./GEO-INFER-SPACE
uv pip install -e ./GEO-INFER-TIME
uv pip install -e ./GEO-INFER-DATA
uv pip install -e ./GEO-INFER-ACT
```

### Step 4: Install Additional Modules

Install domain-specific modules as needed (see the full module table below).

## Per-Module Installation

All 44 modules and their install commands:

### Analytical Core

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-MATH | `uv pip install -e ./GEO-INFER-MATH` | Mathematical foundations, spatial statistics |
| GEO-INFER-ACT | `uv pip install -e ./GEO-INFER-ACT` | Active Inference engine |
| GEO-INFER-BAYES | `uv pip install -e ./GEO-INFER-BAYES` | Bayesian inference, MCMC, variational methods |
| GEO-INFER-AI | `uv pip install -e ./GEO-INFER-AI` | Machine learning and deep learning |
| GEO-INFER-COG | `uv pip install -e ./GEO-INFER-COG` | Cognitive modeling |
| GEO-INFER-AGENT | `uv pip install -e ./GEO-INFER-AGENT` | Multi-agent systems |
| GEO-INFER-SPM | `uv pip install -e ./GEO-INFER-SPM` | Statistical parametric mapping |

### Spatial-Temporal

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-SPACE | `uv pip install -e ./GEO-INFER-SPACE` | Spatial indexing and operations |
| GEO-INFER-TIME | `uv pip install -e ./GEO-INFER-TIME` | Temporal analysis |
| GEO-INFER-IOT | `uv pip install -e ./GEO-INFER-IOT` | IoT sensor integration |

### Infrastructure

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-DATA | `uv pip install -e ./GEO-INFER-DATA` | Data management |
| GEO-INFER-API | `uv pip install -e ./GEO-INFER-API` | API interfaces |
| GEO-INFER-SEC | `uv pip install -e ./GEO-INFER-SEC` | Security |
| GEO-INFER-OPS | `uv pip install -e ./GEO-INFER-OPS` | Deployment and operations |
| GEO-INFER-METAGOV | `uv pip install -e ./GEO-INFER-METAGOV` | Meta-governance |

### Domain-Specific

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-AG | `uv pip install -e ./GEO-INFER-AG` | Agriculture |
| GEO-INFER-HEALTH | `uv pip install -e ./GEO-INFER-HEALTH` | Health and epidemiology |
| GEO-INFER-ECON | `uv pip install -e ./GEO-INFER-ECON` | Economics and markets |
| GEO-INFER-RISK | `uv pip install -e ./GEO-INFER-RISK` | Risk assessment |
| GEO-INFER-LOG | `uv pip install -e ./GEO-INFER-LOG` | Logistics |
| GEO-INFER-BIO | `uv pip install -e ./GEO-INFER-BIO` | Ecology and biology |
| GEO-INFER-CLIMATE | `uv pip install -e ./GEO-INFER-CLIMATE` | Climate analysis |
| GEO-INFER-ENERGY | `uv pip install -e ./GEO-INFER-ENERGY` | Energy systems |
| GEO-INFER-FOREST | `uv pip install -e ./GEO-INFER-FOREST` | Forest management |
| GEO-INFER-MARINE | `uv pip install -e ./GEO-INFER-MARINE` | Marine and ocean |
| GEO-INFER-EMERGENCY | `uv pip install -e ./GEO-INFER-EMERGENCY` | Emergency response |
| GEO-INFER-EDU | `uv pip install -e ./GEO-INFER-EDU` | Education |
| GEO-INFER-TRANSPORT | `uv pip install -e ./GEO-INFER-TRANSPORT` | Transportation |
| GEO-INFER-WATER | `uv pip install -e ./GEO-INFER-WATER` | Water resources |

### Agent and Simulation

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-ANT | `uv pip install -e ./GEO-INFER-ANT` | Ant colony optimization |
| GEO-INFER-SIM | `uv pip install -e ./GEO-INFER-SIM` | Simulation environments |

### Community and Applications

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-CIV | `uv pip install -e ./GEO-INFER-CIV` | Urban planning, civic |
| GEO-INFER-PEP | `uv pip install -e ./GEO-INFER-PEP` | People and demographics |
| GEO-INFER-ORG | `uv pip install -e ./GEO-INFER-ORG` | Organizational |
| GEO-INFER-COMMS | `uv pip install -e ./GEO-INFER-COMMS` | Communications |
| GEO-INFER-APP | `uv pip install -e ./GEO-INFER-APP` | Applications and UI |
| GEO-INFER-ART | `uv pip install -e ./GEO-INFER-ART` | Art and creative |

### Governance

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-NORMS | `uv pip install -e ./GEO-INFER-NORMS` | Normative compliance |
| GEO-INFER-REQ | `uv pip install -e ./GEO-INFER-REQ` | Requirements management |

### Operations and Tooling

| Module | Install Command | Description |
|--------|----------------|-------------|
| GEO-INFER-INTRA | `uv pip install -e ./GEO-INFER-INTRA` | Documentation hub |
| GEO-INFER-GIT | `uv pip install -e ./GEO-INFER-GIT` | Git integration |
| GEO-INFER-TEST | `uv pip install -e ./GEO-INFER-TEST` | Test framework |
| GEO-INFER-EXAMPLES | `uv pip install -e ./GEO-INFER-EXAMPLES` | Example code |
| GEO-INFER-PLACE | `uv pip install -e ./GEO-INFER-PLACE` | Place-based analysis |

## System Dependencies

### GDAL

GDAL is required for raster data operations, CRS transformations, and several
geospatial file formats. Install the system library before the Python bindings.

#### Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal

# Set environment variable for Python GDAL bindings
export GDAL_CONFIG=$(which gdal-config)
```

#### macOS (Homebrew)

```bash
brew install gdal

# Verify installation
gdal-config --version
```

#### macOS (Conda)

```bash
conda install -c conda-forge gdal
```

#### Conda (cross-platform)

```bash
conda install -c conda-forge gdal python-gdal
```

#### Verify GDAL

```bash
gdalinfo --version
# Output: GDAL 3.x.x, released YYYY/MM/DD

python3 -c "from osgeo import gdal; print(gdal.__version__)"
```

### H3

H3 is the spatial indexing library used throughout GEO-INFER. Install the
Python bindings for H3 v4:

```bash
uv pip install "h3>=4.0.0"
```

Verify:

```python
import h3
print(h3.__version__)  # Should be 4.x.x

# Quick functional test
cell = h3.latlng_to_cell(45.5231, -122.6765, 9)
print(f"Test cell: {cell}")
```

If you see `AttributeError: module 'h3' has no attribute 'latlng_to_cell'`,
you have H3 v3 installed. Upgrade:

```bash
uv pip install --upgrade "h3>=4.0.0"
```

### PROJ

PROJ is the coordinate transformation library. It is usually installed as a
GDAL dependency.

```bash
# Ubuntu/Debian
sudo apt-get install -y proj-bin libproj-dev

# macOS
brew install proj

# Verify
proj  # Should print PROJ usage information
```

## Optional Dependencies

These are needed only for specific modules or features:

### Visualization

```bash
# Interactive maps
uv pip install folium

# Plotting
uv pip install plotly matplotlib

# Web map tiles
uv pip install contextily
```

### Machine Learning (GEO-INFER-AI)

```bash
# TensorFlow (CPU)
uv pip install tensorflow

# PyTorch (CPU)
uv pip install torch torchvision

# Scikit-learn
uv pip install scikit-learn
```

### Bayesian Inference (GEO-INFER-BAYES)

```bash
# PyMC for MCMC
uv pip install pymc

# ArviZ for diagnostics
uv pip install arviz

# TensorFlow Probability
uv pip install tensorflow-probability
```

### Geospatial Analysis

```bash
# Spatial analysis
uv pip install geopandas shapely pyproj fiona

# Raster processing
uv pip install rasterio xarray rioxarray

# Network analysis
uv pip install networkx osmnx
```

## Verification Script

Run this script to verify your installation:

```python
#!/usr/bin/env python3
"""GEO-INFER installation verification script."""

import sys
import importlib

CORE_MODULES = [
    ("geo_infer_math", "GEO-INFER-MATH"),
    ("geo_infer_space", "GEO-INFER-SPACE"),
    ("geo_infer_time", "GEO-INFER-TIME"),
    ("geo_infer_data", "GEO-INFER-DATA"),
    ("geo_infer_act", "GEO-INFER-ACT"),
]

DEPENDENCIES = [
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("geopandas", "geopandas"),
    ("shapely", "shapely"),
    ("h3", "h3"),
]

def check_module(import_name: str, display_name: str) -> bool:
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "unknown")
        print(f"  [OK] {display_name}: {version}")
        return True
    except ImportError as e:
        print(f"  [FAIL] {display_name}: {e}")
        return False

def check_h3_v4() -> bool:
    try:
        import h3
        # Test v4 API
        cell = h3.latlng_to_cell(45.5231, -122.6765, 9)
        lat, lng = h3.cell_to_latlng(cell)
        print(f"  [OK] H3 v4 API functional (test cell: {cell})")
        return True
    except AttributeError:
        print("  [FAIL] H3 v3 detected -- upgrade to h3>=4.0.0")
        return False
    except ImportError:
        print("  [FAIL] H3 not installed")
        return False

def main():
    print("GEO-INFER Installation Verification")
    print("=" * 50)
    print(f"Python: {sys.version}")
    print()

    print("Dependencies:")
    dep_ok = all(check_module(imp, name) for imp, name in DEPENDENCIES)
    print()

    print("H3 v4 API:")
    h3_ok = check_h3_v4()
    print()

    print("Core Modules:")
    core_ok = all(check_module(imp, name) for imp, name in CORE_MODULES)
    print()

    if dep_ok and h3_ok and core_ok:
        print("All checks passed.")
    else:
        print("Some checks failed. See above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save this as `verify_install.py` and run:

```bash
uv run python verify_install.py
```

## Troubleshooting

### GDAL Not Found

**Symptom**: `ModuleNotFoundError: No module named 'osgeo'` or
`ERROR: Could not find GDAL library`.

**Solution**: Install the system GDAL library first, then the Python bindings:

```bash
# Ubuntu/Debian
sudo apt-get install -y gdal-bin libgdal-dev
uv pip install GDAL==$(gdal-config --version)

# macOS
brew install gdal
uv pip install GDAL==$(gdal-config --version)
```

### H3 v3 vs v4 API Error

**Symptom**: `AttributeError: module 'h3' has no attribute 'latlng_to_cell'`

**Cause**: H3 v3 is installed. The v3 API uses different function names
(geo_to_h3, h3_to_geo) which are not compatible with GEO-INFER.

**Solution**:

```bash
uv pip install --upgrade "h3>=4.0.0"
```

Verify:

```python
import h3
print(h3.__version__)  # Must be 4.x.x
h3.latlng_to_cell(0, 0, 0)  # Should work without error
```

### Import Errors with Optional Dependencies

**Symptom**: `ImportError: cannot import name 'SomeClass' from 'geo_infer_module'`

**Cause**: GEO-INFER modules use graceful degradation via try/except imports.
If an optional dependency is missing, the classes that depend on it will not be
exported from `__init__.py`.

**Solution**: Install the optional dependency listed in the error message:

```bash
# Check what is available
python3 -c "import geo_infer_act; print(geo_infer_act.__all__)"

# If __all__ is empty, install dependencies
uv pip install numpy scipy
uv pip install -e ./GEO-INFER-ACT
```

### Virtual Environment Conflicts

**Symptom**: Conflicting package versions, `pip` and `uv` package collisions,
or unexpected module versions.

**Solution**: Create a fresh virtual environment:

```bash
# Remove existing venv
rm -rf .venv

# Create fresh venv with uv
uv venv
source .venv/bin/activate

# Reinstall
uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE ./GEO-INFER-ACT
```

### Apple Silicon (M1/M2/M3) Issues

**Symptom**: Build failures or segfaults on Apple Silicon Macs.

**Solution**: Ensure you are using native ARM Python, not Rosetta:

```bash
python3 -c "import platform; print(platform.machine())"
# Should print "arm64", not "x86_64"

# If x86_64, reinstall Python natively:
brew install python@3.11
```

### Memory Errors During Large Operations

**Symptom**: `MemoryError` or system kill when processing large datasets.

**Solution**: Use chunked processing and appropriate data formats:

```python
# Read large GeoParquet in chunks
import geopandas as gpd

# Use row-group-based reading
gdf = gpd.read_parquet("large_data.parquet", columns=["geometry", "value"])

# Process in spatial chunks using H3
import h3
cells = list(h3.grid_disk(center_cell, 5))
for cell_batch in [cells[i:i+10] for i in range(0, len(cells), 10)]:
    subset = gdf[gdf["h3_index"].isin(cell_batch)]
    # Process subset
```

## Development Environment Setup

For contributors developing GEO-INFER modules:

```bash
# Clone and set up
git clone https://github.com/activeinference/GEO-INFER.git
cd GEO-INFER
uv venv
source .venv/bin/activate

# Install dev dependencies
uv pip install black isort mypy flake8 pytest pytest-cov

# Install modules in editable mode
uv pip install -e ./GEO-INFER-MATH -e ./GEO-INFER-SPACE -e ./GEO-INFER-ACT

# Run tests
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# Format code
black GEO-INFER-MATH/src/
isort GEO-INFER-MATH/src/

# Type check
mypy GEO-INFER-MATH/src/
```

## Updating GEO-INFER

```bash
cd GEO-INFER
git pull origin main

# Reinstall updated modules
uv pip install -e ./GEO-INFER-MATH -e ./GEO-INFER-SPACE -e ./GEO-INFER-ACT

# Run verification
uv run python verify_install.py
```

## Related Documentation

- [Overview](overview.md) -- framework architecture
- [Geospatial Standards](geospatial_standards.md) -- H3, CRS, and format details
- [Data Dictionary](data_dictionary.md) -- data structure reference
- [Examples Gallery](examples_gallery.md) -- runnable examples
