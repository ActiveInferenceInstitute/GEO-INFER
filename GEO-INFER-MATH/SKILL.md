---
name: geo-infer-math
description: Spatial statistics, topology, and graph theory for geospatial analysis. Use when computing Moran's I, spatial autocorrelation, geodesic distances, graph connectivity, kernel density estimation, or any mathematical operation on geographic data.
prerequisites:
  required: []
  recommended: []
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-MATH

## Instructions

Foundation module with zero internal dependencies. Provides mathematical primitives consumed by all other modules.

### Core Capabilities

- **Spatial statistics**: Moran's I, Geary's C, Getis-Ord G*, LISA, semivariograms
- **Topology**: Voronoi tessellation, Delaunay triangulation, spatial indexing
- **Graph theory**: Network analysis, shortest paths, centrality measures
- **Kernel density**: Gaussian, Epanechnikov, adaptive bandwidth KDE
- **Distance metrics**: Haversine, Vincenty, geodesic on WGS84 ellipsoid

### Key Imports

```python
from geo_infer_math.core.spatial_statistics import MoranI, GearysC, GetisOrd
from geo_infer_math.core.topology import VoronoiTessellation, DelaunayTriangulation
from geo_infer_math.core.graph_theory import SpatialGraph, CentralityAnalyzer
from geo_infer_math.core.kernel_density import KernelDensityEstimator
```

## Examples

```python
from geo_infer_math.core.spatial_statistics import MoranI
import numpy as np

values = np.random.randn(100)
weights = np.random.rand(100, 100)
moran = MoranI(values, weights)
result = moran.compute()
print(f"Moran's I: {result.statistic}, p-value: {result.p_value}")
```

## Guidelines

- All distance calculations default to WGS84 ellipsoid
- Weight matrices should be row-standardized for spatial statistics
- This module has no external geo-dependencies — pure numpy/scipy
- Test: `uv run python -m pytest GEO-INFER-MATH/tests/ -v`

### Integrations

- **BAYES** → Spatial statistics feeding Bayesian priors
- **SPACE** → H3 spatial weights for autocorrelation
- **SPM** → Statistical parametric map computation
- **AI** → Spatial feature engineering for ML
- **EDU** → Spatial statistics teaching exercises
