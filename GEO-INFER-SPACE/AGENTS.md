# GEO-INFER-SPACE: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-SPACE** module provides core spatial capabilities for agents via backend-agnostic interfaces (indexing, geometry, analytics) and H3 v4 convenience wrappers.

## Agent Capabilities

### 1. H3 Spatial Indexing

```python
from geo_infer_space import SpatialIndexingInterface

indexer = SpatialIndexingInterface(backend="h3")

cell = indexer.latlng_to_cell(37.7749, -122.4194, 9)
lat, lng = indexer.cell_to_latlng(cell)

print(cell)
print((lat, lng))```

### 2. Spatial analytics

```python
from geo_infer_space import SpatialAnalyticsInterface

analytics = SpatialAnalyticsInterface()
result = analytics.analyze_hotspots(spatial_data)
print(result)
```

### 3. Geometric Operations

```python
from geo_infer_space import GeometricOperationsInterface

# Geometric operations
ops = GeometricOperationsInterface()

buffered = ops.buffer(geometry, distance=100)
intersection = ops.intersection(layer_a, layer_b)
union = ops.union([layer_a, layer_b])
```

### 3.1 Unified GIS Submodule Facade

```python
from geo_infer_space import GISManager

# Access all integrated vector, raster, indexing and analytics capabilities
gis = GISManager()

# Run full proximity and distance calculations dynamically
d = gis.calculate_distance((37.7, -122.4), (34.0, -118.2), method="haversine")
buffered_df = gis.buffer_analysis(df, buffer_distance=5.0)
```

### 4. Coordinate Transforms

```python
from geo_infer_space import GISManager

gis = GISManager()
transformed = gis.transform_coordinates(data, from_crs="EPSG:4326", to_crs="EPSG:3857")
```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **H3 Indexing** | ✅ Ready | Hexagonal grid |
| **Analytics** | ✅ Ready | Hotspots, clustering, interpolation (backend-dependent) |
| **Geometry** | ✅ Ready | Buffer, union, intersection |
| **Projections** | ✅ Ready | CRS transforms (via GIS facade / geometry ops) |

### Aspirational Features

- 🔮 **SpatialReasoningAgent**: Spatial logic
- 🔮 **TopologyAgent**: Relationship inference

---

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
