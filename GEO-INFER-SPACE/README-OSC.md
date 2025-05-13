# OS Climate Integration for GEO-INFER-SPACE

This module provides integration with OS Climate geospatial tools within the GEO-INFER-SPACE framework, following the standardized modular structure of the GEO-INFER project.

## Quick Start

```bash
# Install the package
cd GEO-INFER-SPACE
pip install -e .

# Check the status of repositories
osc_status

# Or use programmatically
python -c "from geo_infer_space.osc_geo.utils import check_repo_status, generate_summary; print(generate_summary(check_repo_status()))"
```

## Repository Structure

The OS Climate integration follows the GEO-INFER modular structure:

```
GEO-INFER-SPACE/
├── bin/                       # Command-line scripts
│   └── osc_status            # Script to check repository status
├── src/                       # Source code
│   └── geo_infer_space/       # Package code
│       └── osc_geo/           # OS Climate integration
│           ├── __init__.py
│           └── utils/         # Utility functions
│               ├── __init__.py
│               ├── osc_simple_status.py
│               ├── osc_status.py
│               ├── osc_diagnostics.py
│               ├── osc_wrapper.py
│               └── osc_setup_all.py
├── ext/                       # External repositories
│   └── os-climate/            # OS Climate repositories
│       ├── osc-geo-h3grid-srv
│       └── osc-geo-h3loader-cli
└── setup.py                   # Package installation
```

## Available Scripts

1. **osc_status**: Command-line script to check the status of OS Climate repositories

## Command-Line Options

### osc_status

```bash
osc_status [--output-file FILE] [--quiet]
```

Options:
- `--output-file FILE`: Path to save the status report JSON file
- `--quiet`: Suppress output to console

## Integration Approach

The integration follows a non-invasive approach:

1. OS Climate repositories are cloned but not modified
2. Each repository has its own isolated virtual environment
3. Python utilities in the `geo_infer_space.osc_geo.utils` module provide a clean API
4. Status checking ensures repositories are correctly set up

For more details on the integration approach, see [OSC-INTEGRATION.md](./OSC-INTEGRATION.md).

## Repository Details

The scripts set up the following repositories:

1. **osc-geo-h3grid-srv**: H3 grid service for geospatial applications
2. **osc-geo-h3loader-cli**: Command-line tool for loading data into H3 grid systems

## Programmatic Usage

You can use the integration from Python code:

```python
# Import the utilities
from geo_infer_space.osc_geo.utils import check_repo_status, generate_summary

# Check the status
status = check_repo_status()
print(generate_summary(status))

# Run diagnostics
from geo_infer_space.osc_geo.utils import run_diagnostics

diagnostics = run_diagnostics()
print(diagnostics)

# Work with the OSC wrapper
from geo_infer_space.osc_geo.utils import OSCWrapper

wrapper = OSCWrapper()
wrapper.setup_repositories()
wrapper.run_checks()
```

## Troubleshooting

If you encounter any issues:

1. Run the status script to get a detailed report:
   ```bash
   osc_status
   ```

2. Check that git and Python 3.9+ are installed

3. Verify your network connection if repositories fail to clone

4. Look for specific error messages in the logs

5. Try importing and using the utilities directly:
   ```python
   from geo_infer_space.osc_geo.utils import check_repo_status
   status = check_repo_status()
   print(status)
   ``` 