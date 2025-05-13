# GEO-INFER Installation Guide

This guide provides detailed instructions for installing and setting up the GEO-INFER framework for different use cases and environments.

## Prerequisites

Before installing GEO-INFER, ensure your system meets these requirements:

### System Requirements

- **Operating System**: Linux (recommended: Ubuntu 20.04+), macOS (10.15+), or Windows 10/11
- **CPU**: 4+ cores recommended for most applications
- **RAM**: 8GB minimum, 16GB+ recommended for larger geospatial datasets
- **Storage**: 20GB+ free space, SSD recommended for performance
- **GPU**: Optional but recommended for deep learning components

### Software Dependencies

- **Python**: Version 3.9+ (3.10 recommended)
- **GDAL**: Version 3.4+ for geospatial data processing
- **PostgreSQL**: Version 13+ with PostGIS extension (required only if using advanced data storage)
- **Node.js**: Version 16+ (required only for web visualization components)
- **Docker**: Version 20+ (optional, for containerized deployment)

### Python Knowledge

GEO-INFER is primarily a Python framework. Basic understanding of Python programming is required, with familiarity in these areas helpful:

- Scientific Python ecosystem (NumPy, Pandas, etc.)
- GeoPandas, Shapely, or other geospatial libraries
- Basic understanding of Bayesian methods and/or probabilistic programming

## Installation Methods

GEO-INFER can be installed using several methods depending on your needs:

### Method 1: Full Framework Installation with pip (Recommended for Most Users)

```bash
# Create and activate a virtual environment
python -m venv geo-infer-env
source geo-infer-env/bin/activate  # On Windows: geo-infer-env\Scripts\activate

# Install the core framework
pip install geo-infer

# Install optional components
pip install geo-infer[visualization]  # Adds visualization capabilities
pip install geo-infer[ml]             # Adds machine learning capabilities
pip install geo-infer[dev]            # Adds development tools
```

### Method 2: From Source (Recommended for Developers)

```bash
# Clone the repository
git clone https://github.com/geo-infer/geo-infer.git
cd geo-infer

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Method 3: Using Docker (Recommended for Production)

```bash
# Pull the official Docker image
docker pull geoinfer/geo-infer:latest

# Run the container
docker run -p 8000:8000 -v /path/to/data:/data geoinfer/geo-infer:latest
```

### Method 4: Individual Module Installation

You can install individual GEO-INFER modules based on your specific needs:

```bash
# Install only specific modules
pip install geo-infer-space geo-infer-time geo-infer-data
```

## System-Specific Instructions

### Linux Setup

1. Install system dependencies:

   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y python3-dev python3-pip gdal-bin libgdal-dev build-essential
   
   # RHEL/CentOS/Fedora
   sudo dnf install -y python3-devel python3-pip gdal gdal-devel
   ```

2. Set up environment variables:

   ```bash
   export GDAL_DATA=$(gdal-config --datadir)
   export PROJ_LIB=/usr/share/proj  # Adjust path as needed
   ```

### macOS Setup

1. Install dependencies using Homebrew:

   ```bash
   brew update
   brew install python gdal postgresql node
   ```

2. Set up environment variables:

   ```bash
   export GDAL_DATA=$(gdal-config --datadir)
   export PROJ_LIB=/usr/local/share/proj  # Adjust path as needed
   ```

### Windows Setup

1. Install Python from the [official website](https://www.python.org/downloads/).

2. Install GDAL using OSGeo4W:
   - Download OSGeo4W installer from https://trac.osgeo.org/osgeo4w/
   - Select Express Install and choose GDAL

3. Set up environment variables:
   - Add Python and GDAL to your PATH
   - Set GDAL_DATA and PROJ_LIB variables

## Database Setup (Optional)

For advanced geospatial data storage and querying, set up PostgreSQL with PostGIS:

### PostgreSQL with PostGIS

```bash
# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib postgis postgresql-13-postgis-3

# Create database
sudo -u postgres createdb geo_infer_db
sudo -u postgres psql -d geo_infer_db -c "CREATE EXTENSION postgis;"
```

Configure GEO-INFER to use PostgreSQL:

```bash
# Set environment variables
export GEO_INFER_DB_HOST=localhost
export GEO_INFER_DB_NAME=geo_infer_db
export GEO_INFER_DB_USER=postgres
export GEO_INFER_DB_PASSWORD=your_password
```

## Verification and Testing

Verify your installation is working correctly:

```bash
# Activate your environment if not already active
source geo-infer-env/bin/activate  # On Windows: geo-infer-env\Scripts\activate

# Run verification script
python -c "import geo_infer; geo_infer.verify_installation()"

# Run basic tests
python -m geo_infer.tests.run_basic_tests
```

## Common Installation Issues

### GDAL Installation Problems

If you encounter issues installing GDAL:

```bash
# Try installing with specific version
pip install GDAL==$(gdal-config --version)
```

### Memory Errors During Installation

If you encounter memory errors during installation:

```bash
# Install with reduced parallel compilation
pip install --no-cache-dir --no-binary :all: geo-infer
```

### Import Errors After Installation

If you see import errors after installation:

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall with verbose output
pip install -v --force-reinstall geo-infer
```

## Development Environment Setup

For contributors and developers:

### Setting Up a Development Environment

```bash
# Clone the repository
git clone https://github.com/geo-infer/geo-infer.git
cd geo-infer

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### IDE Configuration

Recommended VS Code settings:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

## Next Steps

After installation, we recommend:

1. Follow the [Quick Start Tutorial](tutorials/getting_started/index.md)
2. Set up your [Development Environment](developer_guide/environment.md)
3. Explore the [Example Notebooks](examples/index.md)
4. Join the [Community Forum](https://forum.geo-infer.org) for questions and discussions

## Troubleshooting

If you encounter issues not covered in this guide:

- Check the [Troubleshooting Page](troubleshooting/installation.md)
- Search or ask on the [Community Forum](https://forum.geo-infer.org)
- Submit an issue on [GitHub](https://github.com/geo-infer/geo-infer/issues)

## Updating GEO-INFER

To update to the latest version:

```bash
# For pip installation
pip install --upgrade geo-infer

# For development installation
git pull
pip install -e .
``` 