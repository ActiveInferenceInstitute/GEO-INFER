# GEO-INFER-MATH: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-MATH** module provides mathematical foundations for agents, including linear algebra, optimization, and computational geometry for geospatial operations.

## Agent Capabilities

### 1. Spatial Optimization

```python
from geo_infer_math import Optimizer

# Solve spatial optimization
optimizer = Optimizer()

solution = optimizer.solve(
    problem_type="facility_location",
    objectives=["minimize_distance", "maximize_coverage"],
    constraints=constraints)

print(f"Optimal locations: {solution.locations}")
print(f"Coverage: {solution.coverage}%")```

### 2. Computational Geometry

```python
from geo_infer_math import GeometryEngine

# Geometric computations
engine = GeometryEngine()

# Voronoi tessellation
voronoi = engine.voronoi(points=facility_locations)

# Convex hull
hull = engine.convex_hull(points=sample_points)

# Triangulation
triangles = engine.delaunay(points=survey_points)```

### 3. Matrix Operations

```python
from geo_infer_math import MatrixOps

# Spatial matrix operations
matrix = MatrixOps()

# Spatial weights matrix
weights = matrix.spatial_weights(
    geometries=polygons,
    method="queen")

# Eigenvalue decomposition
eigens = matrix.eigendecompose(weights)```

### 4. Interpolation

```python
from geo_infer_math import Interpolator

# Spatial interpolation
interpolator = Interpolator()

surface = interpolator.interpolate(
    points=sample_points,
    method="idw",
    resolution=100)

print(f"Grid size: {surface.shape}")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **Optimization** | ✅ Ready | MILP, heuristics |
| **Geometry** | ✅ Ready | Voronoi, hull, triangulation |
| **Matrix** | ✅ Ready | Spatial weights |
| **Interpolation** | ✅ Ready | IDW, kriging |

### Aspirational Features

- 🔮 **MathSolverAgent**: Problem formulation
- 🔮 **OptimizationAgent**: Auto-tuning

---

**Last Updated**: 2026-01-26
