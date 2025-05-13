# OS Climate Integration for GEO-INFER-SPACE

## Overview

This document outlines the approach for integrating OS Climate (OSC) geospatial repositories with GEO-INFER-SPACE. The integration follows a non-invasive approach that avoids direct modifications to the OS Climate repositories, making it easier to stay in sync with upstream changes.

## Core Principles

1. **Non-invasive integration**: We never modify the OS Climate repositories directly
2. **Dependency management**: Each OSC repository maintains its own isolated virtual environment
3. **Validation**: Automated testing ensures compatibility and functionality
4. **Status reporting**: Clear logging and reporting of repository status

## Repository Structure

```
GEO-INFER-SPACE/
├── ext/os-climate/           # External OSC repositories (cloned)
│   ├── osc-geo-h3grid-srv/   # H3 grid service repository
│   └── osc-geo-h3loader-cli/ # Data loader CLI repository
├── src/geo_infer_space/      # Main package source code
│   └── osc_geo/              # OSC integration module
│       ├── __init__.py       # Integration API
│       ├── grid_service.py   # H3 grid service wrapper
│       ├── data_loader.py    # Data loader wrapper
│       └── utils.py          # Utility functions
├── osc_setup_all.py          # Setup script for OSC repositories
├── osc_wrapper.py            # Simple wrapper to run setup script
└── OSC-INTEGRATION.md        # This documentation file
```

## Integration Approach

### 1. Repository Management

Instead of forking or modifying the OS Climate repositories, we:

1. Clone them into the `ext/os-climate/` directory
2. Create isolated virtual environments within each repository
3. Install dependencies in these environments
4. Run tests to verify functionality
5. Create wrapper modules in our codebase that interact with these repositories

This approach allows us to:
- Stay in sync with upstream changes
- Avoid merge conflicts
- Isolate dependencies
- Clearly separate our code from OSC code

### 2. Runtime Integration

At runtime, the integration works as follows:

1. Wrappers in `src/geo_infer_space/osc_geo/` provide a consistent API for OSC functionality
2. These wrappers manage subprocess calls to the OSC repositories
3. Environment management ensures the correct dependencies are used
4. Data is exchanged through files or network interfaces

### 3. Validation and Reporting

The integration includes:

1. Status reporting through structured logs
2. Validation checks to ensure repositories are properly set up
3. Diagnostic tools for troubleshooting
4. Documentation of common issues and solutions

## Setup and Usage

### Setting Up the Environment

To set up the OS Climate repositories:

```bash
python3 osc_setup_all.py
```

This script will:
1. Clone the repositories if they don't exist
2. Update them if they do exist
3. Install dependencies
4. Run tests to verify functionality
5. Generate a status report

### Verifying Integration Status

To check if the integration is functioning correctly:

```python
from geo_infer_space.osc_geo import check_integration_status

status = check_integration_status()
print(status.summary())
```

The status object contains:
- Repository information (paths, versions)
- Test results
- Configuration status
- Environment details

### Using OSC Functionality

Example usage of the H3 grid service:

```python
from geo_infer_space.osc_geo import create_h3_grid_manager

# Create a grid manager that will handle H3 grid operations
grid_manager = create_h3_grid_manager()

# Start the H3 grid service
grid_manager.start_server()

# Use the grid service
results = grid_manager.process_dataset(dataset_path, resolution=8)

# Stop the server when done
grid_manager.stop_server()
```

## Troubleshooting

### Common Issues

1. **Repository Clone Failures**
   - Check network connectivity
   - Verify GitHub access

2. **Dependency Installation Failures**
   - Check Python version (3.9+ required)
   - Verify system dependencies (OpenSSL, etc.)

3. **Test Failures**
   - Check the specific test failure messages
   - Verify environment variables and settings

### Diagnostic Tools

The integration includes diagnostic tools for troubleshooting:

```python
from geo_infer_space.osc_geo import run_diagnostics

diagnostics = run_diagnostics()
print(diagnostics.detailed_report())
```

## Updating OSC Repositories

To update the OS Climate repositories to the latest versions:

```bash
python3 osc_setup_all.py --force-clone
```

This will remove the existing repositories and clone them fresh from GitHub. 