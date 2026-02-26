---
title: "GEO-INFER-MATH: Mathematical Foundations"
description: "Linear algebra, optimization, and computational geometry for geospatial operations"
purpose: "Provide mathematical primitives and algorithms for spatial computation"
module_type: "Core Infrastructure"
status: "Stable"
last_updated: "2026-02-25"
dependencies: []
compatibility: ["All GEO-INFER modules"]
tags: ["math", "optimization", "geometry", "linear-algebra", "algorithms"]
difficulty: "Advanced"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-MATH: Mathematical Foundations

## Overview

**GEO-INFER-MATH** provides mathematical primitives for geospatial computation:

- **Optimization**: Spatial optimization algorithms (MILP, heuristics)
- **Computational Geometry**: Voronoi, Delaunay, convex hull
- **Linear Algebra**: Matrix operations, decompositions
- **Interpolation**: IDW, kriging, spline methods

## Features

### Spatial Optimization

```python
from geo_infer_math import OptimizationManager, create_optimization_manager

# Create optimization manager for facility location
manager = create_optimization_manager()

result = manager.optimize(
    objective_function=facility_cost_function,
    bounds=search_bounds,
    method="scipy"
)

print(f"Optimal parameters: {result['solution']}")
print(f"Minimum cost: {result['value']}")
```

### Computational Geometry

```python
from geo_infer_math import Point, Polygon, haversine_distance, point_in_polygon

# Create geometric primitives
p1 = Point(x=-122.4194, y=37.7749)
p2 = Point(x=-118.2437, y=34.0522)

# Calculate distances
dist = haversine_distance(p1.y, p1.x, p2.y, p2.x)
print(f"Distance: {dist:.1f} km")

# Polygon operations
poly = Polygon(exterior=[Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)])
area = poly.area()
print(f"Area: {area}")
```

### Matrix Operations

```python
from geo_infer_math import MatrixOperations
import numpy as np

# Matrix operations for spatial analysis
matrix = np.array([[4, 2], [2, 3]])

# Check matrix properties
cond = MatrixOperations.condition_number(matrix)
is_pd = MatrixOperations.is_positive_definite(matrix)

print(f"Condition number: {cond:.2f}")
print(f"Positive definite: {is_pd}")
```

### Interpolation

```python
from geo_infer_math import IDWInterpolator, KrigingInterpolator, InterpolationConfig

# IDW interpolation
idw = IDWInterpolator(config=InterpolationConfig(power=2.0))
idw.fit(coordinates=sample_coords, values=measurements)
surface_idw = idw.predict(grid_coords)

# Kriging interpolation
kriging = KrigingInterpolator(config=InterpolationConfig(variogram_model="spherical"))
kriging.fit(coordinates=sample_coords, values=measurements)
surface_krig = kriging.predict(grid_coords)
```

## Algorithms

| Category | Algorithms |
|----------|------------|
| **Optimization** | Simplex, Branch & Bound, Genetic, Simulated Annealing |
| **Geometry** | Voronoi, Delaunay, Hull, Intersection |
| **Graph** | Dijkstra, A*, Floyd-Warshall |
| **Statistics** | PCA, Clustering, Regression |

## Optimization Problems

| Problem | Application |
|---------|-------------|
| **P-Median** | Facility location |
| **TSP** | Vehicle routing |
| **Maximal Coverage** | Service area planning |
| **Set Covering** | Resource allocation |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-SPACE** | Geometric operations |
| **GEO-INFER-SPM** | Statistical methods |
| **GEO-INFER-LOG** | Route optimization |

## Installation

```bash
uv pip install -e "./GEO-INFER-MATH"
```

## Use Cases

### Optimal Facility Placement

```python
from geo_infer_math import OptimizationManager, OptimizationConfig

manager = OptimizationManager(config=OptimizationConfig(max_iterations=500))

result = manager.optimize(
    objective_function=facility_distance_cost,
    bounds=candidate_bounds,
    method="genetic"
)
```

---

**Status**: Stable

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
