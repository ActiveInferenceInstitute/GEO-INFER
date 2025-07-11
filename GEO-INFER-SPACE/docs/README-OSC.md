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

The OS Climate integration follows the GEO-INFER modular structure, using forks from github.com/docxology:

```
GEO-INFER-SPACE/
├── bin/                       # Command-line scripts
│   ├── osc_setup_all.py       # Setup script
│   ├── osc_status.py          # Status check script
│   ├── osc_wrapper.py         # Wrapper script
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
├── repo/                      # External repositories
│   └── os-climate/            # OS Climate repositories (forked)
│       ├── osc-geo-h3grid-srv
│       └── osc-geo-h3loader-cli
└── setup.py                   # Package installation
```