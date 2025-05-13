# OSC-GEO Module

## Overview

OSC-GEO is a module within GEO-INFER-SPACE that provides integration with OS Climate geospatial tools, focusing on H3 grid systems and geospatial data loading capabilities.

This module enables you to:
- Clone and manage OS Climate geospatial repositories
- Start and interact with H3 grid services
- Load and transform geospatial data into H3 grid systems
- Convert between GeoJSON and H3 formats

## Installation

The OSC-GEO module is installed as part of GEO-INFER-SPACE. Make sure you have [GEO-INFER-GIT](../../GEO-INFER-GIT) installed as it's required for repository cloning functionality.

## Dependencies

- GEO-INFER-GIT: For repository cloning
- h3-py: For H3 geospatial operations
- fastapi: For REST API capabilities

## Getting Started

### Setting Up the Module

First, you need to clone the OS Climate repositories:

```python
from geo_infer_space.osc_geo import setup_osc_geo

# Clone the necessary repositories
result = setup_osc_geo()
print(f"Repositories cloned successfully: {all(result.values())}")
```

### Using the H3 Grid Manager

Start and interact with the H3 grid service:

```python
from geo_infer_space.osc_geo import create_h3_grid_manager

# Create the manager and start the service
grid_manager = create_h3_grid_manager(auto_start=True)

# Check if the service is running
if grid_manager.is_server_running():
    print(f"Grid service running at: {grid_manager.get_api_url()}")

# Stop the service when done
grid_manager.stop_server()
```

### Loading Data into H3 Grid

Transform geospatial data into an H3 grid system:

```python
from geo_infer_space.osc_geo import load_data_to_h3_grid

# Load data into H3 grid
success = load_data_to_h3_grid(
    input_file="path/to/input.geojson",
    output_file="path/to/output.geojson",
    resolution=8,
    format="geojson"
)

if success:
    print("Data loaded successfully")
```

### Converting Between GeoJSON and H3

The module provides utility functions for converting between GeoJSON and H3:

```python
from geo_infer_space.osc_geo.utils import geojson_to_h3, h3_to_geojson

# Convert GeoJSON to H3 indices
with open("path/to/geojson.json", "r") as f:
    geojson_data = f.read()

h3_data = geojson_to_h3(geojson_data, resolution=9)
print(f"Number of H3 indices: {len(h3_data['h3_indices'])}")

# Convert H3 indices back to GeoJSON
geojson = h3_to_geojson(h3_data["h3_indices"], h3_data["properties"])
```

## API Reference

### Core Modules

- [repos.py](./core/repos.md): Repository cloning and management
- [h3grid.py](./core/h3grid.md): H3 grid service management
- [loader.py](./core/loader.md): Data loading and H3 grid generation

### API Modules

- [rest.py](./api/rest.md): REST API for interacting with OSC-GEO functionality

### Utility Modules

- [h3_utils.py](./utils/h3_utils.md): Utility functions for H3 grid operations

## Integration with GEO-INFER-OPS

OSC-GEO is designed to work seamlessly with GEO-INFER-OPS for testing and orchestration:

- Test capabilities are coordinated by GEO-INFER-OPS
- Service orchestration is managed through GEO-INFER-OPS configuration
- Monitoring and logging are integrated with GEO-INFER-OPS infrastructure

For more information on testing and orchestration, see the [GEO-INFER-OPS documentation](../../GEO-INFER-OPS). 