# GEO-INFER-SPACE: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-SPACE** module provides core spatial analysis capabilities for agents, including H3 indexing, geometric operations, and spatial queries.

## Agent Capabilities

### 1. H3 Spatial Indexing

```python
from geo_infer_space import H3Indexer

# Index spatial data with H3
indexer = H3Indexer()

cells = indexer.index(
    geometry=city_boundary,
    resolution=9)

print(f"H3 cells: {len(cells)}")
print(f"Coverage: {cells.coverage}%")```

### 2. Spatial Queries

```python
from geo_infer_space import SpatialQuery

# Perform spatial queries
query = SpatialQuery()

results = query.within(
    features=buildings,
    boundary=flood_zone)

nearby = query.nearby(
    point=location,
    radius_m=1000,
    features=amenities)
```

### 3. Geometric Operations

```python
from geo_infer_space import GeometryOps

# Geometric operations
ops = GeometryOps()

buffered = ops.buffer(geometry, distance=100)
intersection = ops.intersect(layer_a, layer_b)
union = ops.union(polygons)```

### 4. Coordinate Transforms

```python
from geo_infer_space import Projector

# Coordinate transformations
projector = Projector()

transformed = projector.transform(
    geometry=data,
    from_crs="EPSG:4326",
    to_crs="EPSG:3857")
```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **H3 Indexing** | ✅ Ready | Hexagonal grid |
| **Queries** | ✅ Ready | Within, nearby, intersects |
| **Geometry** | ✅ Ready | Buffer, union, intersect |
| **Projections** | ✅ Ready | CRS transforms |

### Aspirational Features

- 🔮 **SpatialReasoningAgent**: Spatial logic
- 🔮 **TopologyAgent**: Relationship inference

---

**Last Updated**: 2026-02-24
