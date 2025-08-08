# Installation Guide

This guide will help you install GEO-INFER on your system. Choose the installation method that best fits your needs and environment.

## 🚀 Quick Installation

### Prerequisites

Before installing GEO-INFER, ensure you have:

- **Python 3.8+** installed on your system
- **uv** (Python package manager)
- **Git** (for development installation)
- **Docker** (for containerized installation)

### Method 1: uv Installation (Recommended)

The simplest way to install GEO-INFER:

```bash
# Install the main package
uv pip install geo-infer

# Install with all optional dependencies
uv pip install 'geo-infer[all]'

# Install specific modules
uv pip install geo-infer-space geo-infer-time geo-infer-act
```

### Method 2: Development Installation (uv)

For developers who want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/geo-infer/geo-infer-intra.git
cd geo-infer-intra

# Install in development mode
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

### Method 3: Docker Installation

For containerized environments:

```bash
# Pull the official image
docker pull geo-infer/geo-infer-intra:latest

# Run the container
docker run -p 8080:8080 geo-infer/geo-infer-intra:latest

# Run with custom configuration
docker run -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  geo-infer/geo-infer-intra:latest
```

## 📦 Detailed Installation

### System Requirements

#### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Linux, macOS, or Windows

#### Recommended Requirements
- **Python**: 3.9 or higher
- **RAM**: 16GB or more
- **Storage**: 10GB free space
- **GPU**: NVIDIA GPU with CUDA support (optional, for acceleration)

### Python Environment Setup

#### Using uv project environments (Recommended)

```bash
# Initialize uv in the project (if needed)
uv init --no-workspace .

# Sync dependencies defined in pyproject.toml
uv sync

# Run Python inside the project environment
uv run python -c "import sys; print(sys.executable)"
```

#### Using conda

```bash
# Create a conda environment
conda create -n geo-infer python=3.9

# Activate the environment
conda activate geo-infer

# Install GEO-INFER
pip install geo-infer
```

#### Using pyenv

```bash
# Install Python 3.9
pyenv install 3.9.12

# Set local Python version
pyenv local 3.9.12

# Create virtual environment
python -m venv geo-infer-env
source geo-infer-env/bin/activate

# Install GEO-INFER
pip install geo-infer
```

### Module-Specific Installation

Install only the modules you need:

```bash
# Core modules
pip install geo-infer-space    # Spatial analysis
pip install geo-infer-time     # Temporal analysis
pip install geo-infer-act      # Active inference
pip install geo-infer-bayes    # Bayesian inference

# Domain-specific modules
pip install geo-infer-ag       # Agriculture
pip install geo-infer-bio      # Biodiversity
pip install geo-infer-civ      # Civil infrastructure
pip install geo-infer-econ     # Economics
pip install geo-infer-risk     # Risk assessment

# Optional modules
pip install geo-infer-sim      # Simulation
pip install geo-infer-agent    # Agent modeling
pip install geo-infer-cog      # Cognitive modeling
```

### Dependencies Installation

#### System Dependencies (Linux)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libgeos-dev \
    libproj-dev \
    libgdal-dev \
    libspatialindex-dev \
    libhdf5-dev \
    libnetcdf-dev

# CentOS/RHEL
sudo yum install -y \
    gcc \
    gcc-c++ \
    geos-devel \
    proj-devel \
    gdal-devel \
    spatialindex-devel \
    hdf5-devel \
    netcdf-devel
```

#### System Dependencies (macOS)

```bash
# Using Homebrew
brew install geos proj gdal spatialindex hdf5 netcdf

# Using MacPorts
sudo port install geos proj gdal spatialindex hdf5 netcdf
```

#### System Dependencies (Windows)

For Windows, most dependencies are included in the Python packages. If you encounter issues:

1. Install [OSGeo4W](https://trac.osgeo.org/osgeo4w/)
2. Install [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Optional Dependencies

#### GPU Support (CUDA)

```bash
# Install CUDA toolkit (if not already installed)
# Follow NVIDIA's installation guide for your system

# Install PyTorch with CUDA support
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other GPU-accelerated libraries
pip install cupy-cuda11x  # For NumPy-like operations on GPU
```

#### Database Support

```bash
# PostgreSQL support
uv pip install psycopg2-binary

# MongoDB support
uv pip install pymongo

# Redis support
uv pip install redis

# SQLite support (usually included)
uv pip install sqlite3
```

#### Cloud Storage Support

```bash
# AWS S3 support
uv pip install boto3

# Google Cloud Storage support
uv pip install google-cloud-storage

# Azure Blob Storage support
uv pip install azure-storage-blob
```

## 🔧 Configuration

### Environment Variables

Set these environment variables for optimal performance:

```bash
# Set in your shell profile (.bashrc, .zshrc, etc.)
export GEO_INFER_DATA_DIR="/path/to/data"
export GEO_INFER_CACHE_DIR="/path/to/cache"
export GEO_INFER_LOG_LEVEL="INFO"
export GEO_INFER_MAX_WORKERS="4"
```

### Configuration File

Create a configuration file at `~/.geo-infer/config.yaml`:

```yaml
# Data directories
data:
  base_dir: "/path/to/data"
  cache_dir: "/path/to/cache"
  temp_dir: "/tmp/geo-infer"

# Performance settings
performance:
  max_workers: 4
  memory_limit: "8GB"
  cache_size: "2GB"

# Logging
logging:
  level: "INFO"
  file: "/path/to/logs/geo-infer.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# API settings
api:
  host: "localhost"
  port: 8080
  debug: false
  cors_origins: ["http://localhost:3000"]

# Database settings
database:
  url: "postgresql://user:password@localhost:5432/geo_infer"
  pool_size: 10
  max_overflow: 20
```

## ✅ Verification

### Basic Installation Test

```python
# Test basic installation
import geo_infer_space
import geo_infer_time
import geo_infer_act

print("✅ GEO-INFER installed successfully!")

# Test spatial functionality
from geo_infer_space import SpatialAnalyzer
analyzer = SpatialAnalyzer()
print("✅ Spatial analysis module working!")

# Test temporal functionality
from geo_infer_time import TemporalAnalyzer
temporal = TemporalAnalyzer()
print("✅ Temporal analysis module working!")

# Test active inference
from geo_infer_act import ActiveInferenceModel
model = ActiveInferenceModel()
print("✅ Active inference module working!")
```

### Performance Test

```python
# Test performance with sample data
import time
from geo_infer_space import SpatialAnalyzer

# Create sample data
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# Generate 1000 random points
np.random.seed(42)
n_points = 1000
lats = np.random.uniform(30, 50, n_points)
lons = np.random.uniform(-120, -70, n_points)
points = [Point(lon, lat) for lon, lat in zip(lons, lats)]
gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")

# Test spatial analysis performance
start_time = time.time()
analyzer = SpatialAnalyzer()
result = analyzer.analyze_points(gdf)
end_time = time.time()

print(f"✅ Performance test completed in {end_time - start_time:.2f} seconds")
```

### GPU Test (if applicable)

```python
# Test GPU support
try:
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA version: {torch.version.cuda}")
    else:
        print("⚠️  GPU not available, using CPU")
except ImportError:
    print("⚠️  PyTorch not installed, GPU acceleration not available")
```

## 🚨 Troubleshooting

### Common Installation Issues

#### Issue: GDAL Installation Problems

**Symptoms**: `ImportError: No module named 'osgeo'` or similar

**Solutions**:

```bash
# On Ubuntu/Debian
sudo apt-get install python3-gdal

# On macOS with Homebrew
brew install gdal
pip install GDAL

# On Windows
# Download GDAL wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/
pip install GDAL-3.4.3-cp39-cp39-win_amd64.whl
```

#### Issue: GEOS Installation Problems

**Symptoms**: `ImportError: No module named 'shapely'` or similar

**Solutions**:

```bash
# Install GEOS system library
# On Ubuntu/Debian:
sudo apt-get install libgeos-dev

# On macOS:
brew install geos

# Reinstall shapely
pip uninstall shapely
pip install shapely
```

#### Issue: Memory Issues

**Symptoms**: `MemoryError` or slow performance

**Solutions**:

```python
# Set memory limits in your code
import os
os.environ['GEO_INFER_MEMORY_LIMIT'] = '4GB'

# Use chunked processing for large datasets
from geo_infer_space import SpatialAnalyzer
analyzer = SpatialAnalyzer(chunk_size=1000)
```

#### Issue: CUDA/GPU Problems

**Symptoms**: GPU not detected or CUDA errors

**Solutions**:

```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Platform-Specific Issues

#### Windows Issues

1. **Visual C++ Build Tools**: Install Microsoft Visual C++ Build Tools
2. **PATH Issues**: Add Python and pip to system PATH
3. **Permission Issues**: Run as administrator or use virtual environments

#### macOS Issues

1. **Xcode Command Line Tools**: Install with `xcode-select --install`
2. **Homebrew**: Install missing dependencies with `brew install`
3. **Permission Issues**: Use virtual environments to avoid permission problems

#### Linux Issues

1. **System Dependencies**: Install required system libraries
2. **Python Version**: Ensure Python 3.8+ is installed
3. **User Permissions**: Use virtual environments or install with `--user` flag

### Getting Help

If you encounter issues not covered here:

1. **Check the [FAQ](../support/faq.md)** for common solutions
2. **Search [GitHub Issues](https://github.com/geo-infer/geo-infer-intra/issues)** for similar problems
3. **Ask on the [Community Forum](https://forum.geo-infer.org)**
4. **Create a new issue** with detailed error information

## 🔄 Updating

### Update GEO-INFER

```bash
# Update to latest version
uv pip install --upgrade geo-infer

# Update specific modules
uv pip install --upgrade geo-infer-space geo-infer-time

# Update from development repository
cd geo-infer-intra
git pull origin main
uv pip install -e .
```

### Check Version

```python
import geo_infer_space
import geo_infer_time
import geo_infer_act

print(f"GEO-INFER-SPACE version: {geo_infer_space.__version__}")
print(f"GEO-INFER-TIME version: {geo_infer_time.__version__}")
print(f"GEO-INFER-ACT version: {geo_infer_act.__version__}")
```

## 🎯 Next Steps

After successful installation:

1. **[Run Your First Analysis](first_analysis.md)** - Complete a simple geospatial analysis
2. **[Explore the API](../api/index.md)** - Learn the programming interface
3. **[Follow Tutorials](../tutorials/index.md)** - Step-by-step guides
4. **[Join the Community](https://forum.geo-infer.org)** - Connect with other users

---

**Need help?** Check the [Troubleshooting Guide](../support/troubleshooting.md) or ask on the [Community Forum](https://forum.geo-infer.org). 