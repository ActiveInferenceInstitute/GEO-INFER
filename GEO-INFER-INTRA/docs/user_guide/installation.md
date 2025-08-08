# Installation Guide

This guide provides detailed instructions for installing GEO-INFER-INTRA on various platforms.

## Prerequisites

Before installing GEO-INFER-INTRA, ensure that you have the following prerequisites:

- Python 3.9 or higher
- uv (Python package manager)
- Git
- Node.js 16 or higher (for UI components)
- Docker (optional, for containerized deployment)

## Installation Methods

GEO-INFER-INTRA can be installed using one of the following methods:

### Method 1: Install from PyPI

```bash
# Initialize a project environment (if not already)
uv init --no-workspace .

# Install the package
uv pip install geo-infer-intra
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/geo-infer/geo-infer-intra.git
cd geo-infer-intra

# Install in development mode
uv pip install -e .

# Install development dependencies (optional)
uv pip install -e ".[dev]"
```

### Method 3: Install with Docker

```bash
# Pull the Docker image
docker pull geoinfer/geo-infer-intra:latest

# Run the container
docker run -p 8000:8000 geoinfer/geo-infer-intra:latest
```

## Post-Installation Setup

After installing GEO-INFER-INTRA, complete the following setup steps:

1. Create a configuration file:
   ```bash
   cp config/example.yaml config/local.yaml
   ```

2. Edit the configuration file with your settings:
   ```bash
   nano config/local.yaml  # or use any text editor
   ```

3. Initialize the knowledge base:
   ```bash
   uv run geo-infer-intra init
   ```

4. Start the documentation server:
   ```bash
   uv run geo-infer-intra docs serve
   ```

## Verifying the Installation

To verify that GEO-INFER-INTRA is installed correctly:

1. Access the documentation web interface at `http://localhost:8000`
2. Run the version check command:
   ```bash
   uv run geo-infer-intra --version
   ```
3. Run the system check:
   ```bash
   uv run geo-infer-intra check
   ```

## Troubleshooting

If you encounter issues during installation:

- Check that all prerequisites are installed (including `uv`)
- Ensure that you have sufficient permissions
- Verify that your Python version is compatible
- Check the logs in `logs/installation.log`
- See the [Troubleshooting Guide](troubleshooting.md) for more information

## Next Steps

After installing GEO-INFER-INTRA, see the [Configuration](configuration.md) guide for information on configuring the system, and the [Getting Started](getting_started.md) guide for instructions on using the system. 