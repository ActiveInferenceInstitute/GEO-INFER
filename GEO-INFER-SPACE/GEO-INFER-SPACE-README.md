# GEO-INFER-SPACE

## Overview
GEO-INFER-SPACE provides advanced spatial methods for land, water, air, and more within the GEO-INFER framework. This module delivers powerful geospatial capabilities for analyzing and understanding spatial relationships across various domains.

## Key Features
- Multi-resolution spatial indexing (e.g., H3 hexagonal grids)
- Real-time geospatial analytics using IoT and edge computing
- Support for Earth Observation data via STAC protocols
- Advanced spatial operations and algorithms
- OS Climate integration for geospatial data processing

## Directory Structure
```
GEO-INFER-SPACE/
├── docs/                   # Documentation
├── examples/               # Example use cases
├── ext/os-climate/         # Cloned OS Climate repositories
├── src/                    # Source code
│   └── geo_infer_space/    # Main package
│       ├── api/            # API definitions
│       ├── analytics/      # Spatial analytics algorithms
│       ├── core/           # Core functionality
│       ├── indexing/       # Spatial indexing systems
│       ├── io/             # Input/output operations
│       ├── models/         # Data models
│       ├── osc_geo/        # OS Climate integration module
│       └── utils/          # Utility functions
├── tests/                  # Test suite
├── osc_setup_all.py        # Script to set up OS Climate repositories
├── osc_status.py           # Script to check OS Climate repositories status
├── osc_wrapper.py          # Wrapper script for setup and status check
└── README-OSC.md           # OS Climate integration documentation
```

## Getting Started
1. Installation
   ```bash
   pip install -e .
   ```

2. Configuration
   ```bash
   cp config/example.yaml config/local.yaml
   # Edit local.yaml with your configuration
   ```

3. Running Tests
   ```bash
   pytest tests/
   ```

4. Setting up OS Climate integration
   ```bash
   # Clone, set up, and test OS Climate repositories
   ./osc_wrapper.py
   ```

## Spatial Indexing Systems
GEO-INFER-SPACE implements multiple spatial indexing systems:
- H3 Hexagonal Hierarchical Index
- QuadTree
- R-Tree
- Geohash
- S2 Cells

Each system has different properties and use cases detailed in `docs/indexing.md`.

## Coordinate Reference Systems
The module supports multiple coordinate reference systems:
- WGS84 (EPSG:4326)
- Web Mercator (EPSG:3857)
- UTM zones
- Custom local projections

Transformation between systems is handled automatically with appropriate metadata.

## Spatial Analytics
Advanced spatial analytics capabilities include:
- Proximity analysis
- Clustering and hotspot detection
- Spatial interpolation
- Terrain analysis
- Viewshed analysis
- Network routing
- Spatial statistics

## OS Climate Integration
GEO-INFER-SPACE integrates with OS Climate's geospatial tools:

1. **H3 Grid Service**: Create and manage H3 hexagonal grids
2. **H3 Data Loader**: Load geospatial data into H3 grid systems

To use the OS Climate integration:

```python
from geo_infer_space.osc_geo import create_h3_grid_manager, load_data_to_h3_grid

# Create a grid manager
grid_manager = create_h3_grid_manager(auto_start=True)

# Load data into H3 grid
load_data_to_h3_grid(
    input_file="data/example.geojson",
    output_file="output/h3_data.geojson",
    resolution=8
)
```

For detailed OS Climate integration documentation, see [README-OSC.md](./README-OSC.md).

## Integration with Other Modules
GEO-INFER-SPACE integrates with:
- GEO-INFER-DATA for data access
- GEO-INFER-TIME for spatio-temporal analysis
- GEO-INFER-ACT for active inference modeling
- GEO-INFER-SIM for spatial simulations

## Performance and Scaling
The module implements optimization strategies for different scales of spatial data:
- In-memory operations for small datasets
- Distributed computing for large-scale analysis
- GPU acceleration for raster operations
- Edge computing support for real-time applications

## Contributing
Follow the contribution guidelines in the main GEO-INFER documentation. 