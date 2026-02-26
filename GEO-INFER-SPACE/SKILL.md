---
name: geo-infer-space
description: H3 hexagonal spatial indexing and multi-backend spatial operations. Use when working with H3 cells, spatial indexing, coordinate systems, raster/vector operations, or any spatial backend dispatch (H3, SRAI, PostGIS).
prerequisites:
  required:
    - geo-infer-math
  recommended:
    - geo-infer-data
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-SPACE

## Instructions

### Core Capabilities

- **H3 v4 indexing**: Cell operations, hierarchical resolution, k-ring neighbors
- **Backend dispatch**: Interface pattern for H3, SRAI, PostGIS backends
- **Coordinate systems**: CRS transformations, EPSG management
- **Spatial operations**: Buffers, intersections, unions, containment
- **Visualization**: Choropleth maps, heatmaps, spatial dashboards

### Key Imports

```python
from geo_infer_space.backends.h3 import H3Backend
from geo_infer_space.core.spatial_operations import SpatialEngine
from geo_infer_space.core.coordinate_systems import CRSManager
```

### H3 v4 API (Critical)

```python
import h3
# CORRECT (v4):
cell = h3.latlng_to_cell(lat, lng, resolution)
lat, lng = h3.cell_to_latlng(cell)
neighbors = h3.grid_disk(cell, k)

# WRONG (legacy v3 — never use):
# h3.geo_to_h3(), h3.h3_to_geo(), h3.k_ring()
```

## Examples

```python
from geo_infer_space.backends.h3 import H3Backend

backend = H3Backend()

# Index a point to an H3 cell at resolution 7
cell = backend.latlng_to_cell(45.5231, -122.6765, resolution=7)
print(f"H3 cell: {cell}")

# Get neighbors
neighbors = backend.grid_disk(cell, k=2)
print(f"Neighbors (k=2): {len(neighbors)} cells")

# Tessellate a region
from shapely.geometry import box
region = box(-122.8, 45.4, -122.5, 45.6)
cells = backend.tessellate(region, resolution=8)
print(f"Tessellation: {len(cells)} cells")
```

```python
from geo_infer_space.core.coordinate_systems import CRSManager

crs = CRSManager()
x, y = crs.transform(45.5, -122.6, from_epsg=4326, to_epsg=32610)
print(f"UTM Zone 10N: ({x:.0f}, {y:.0f})")
```

## Guidelines

- Always use H3 v4 API — zero legacy calls allowed
- Backend-agnostic: use the dispatcher pattern, not direct H3 calls
- EPSG:4326 (WGS84) is the default CRS
- Test: `uv run python -m pytest GEO-INFER-SPACE/tests/ -v`

### Integrations

- **MATH** → Spatial weights for statistics
- **TIME** → Spatio-temporal analysis
- **DATA** → Spatial indexing of datasets
- **PLACE** → Boundary tessellation with H3
- Nearly every module depends on SPACE for geographic indexing
