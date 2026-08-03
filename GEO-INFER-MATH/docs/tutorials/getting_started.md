# Getting Started with GEO-INFER-MATH

This tutorial demonstrates the core functionality of the MATH module:
geometric operations and spatial statistics. The examples below were verified
against the current package exports.

## Installation

GEO-INFER-MATH is part of the GEO-INFER uv workspace. Install from a clone:

```bash
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER
uv sync --package geo-infer-math
```

## Geometric Calculations

```
```python
from geo_infer_math import haversine_distance, Point

# Distance between New York and Los Angeles
distance = haversine_distance(
    lat1=40.7128, lon1=-74.0060,
    lat2=34.0522, lon2=-118.2437,
)
print(f"Distance between New York and Los Angeles: {distance:.2f} km")
# Output: Distance between New York and Los Angeles: 3935.75 km

# Euclidean distance between two points
point1 = Point(x=10, y=20)
point2 = Point(x=13, y=24)
print(f"Euclidean distance: {point1.distance_to(point2):.2f}")
# Output: Euclidean distance: 5.00
```

## Spatial Statistics

```
```python
import numpy as np
from geo_infer_math import MoranI

# Two spatially separated clusters
coords = np.array([
    [0, 0], [1, 0], [0, 1], [1, 1],      # Cluster 1
    [10, 10], [11, 10], [10, 11], [11, 11],  # Cluster 2
])
values = np.array([10, 12, 11, 13, 50, 52, 51, 53])

moran = MoranI()
result = moran.compute(values, coords)
print(f"Moran's I: {result['I']:.4f} (p-value: {result['p_value']:.4f})")
# Output: Moran's I: 0.8078 (p-value: 0.0001)
```

Other exports include `GearysC`, `GetisOrd`, `getis_ord_g`, `ripley_k`,
`semivariogram`, and `spatial_descriptive_statistics`; see the module's
`__init__.py` for the full public surface.

## The Spatial Analysis API

The `geo_infer_math.api.spatial_analysis` module provides a request/response
API (`SpatialAnalysisAPI`, `AutocorrelationRequest`, `InterpolationRequest`,
etc.) for descriptive statistics, autocorrelation, hotspot analysis,
clustering, and interpolation:

```
```python
from geo_infer_math.api.spatial_analysis import SpatialAnalysisAPI

api = SpatialAnalysisAPI()
```

## Interpolation

`geo_infer_math.core.interpolation` provides `SpatialInterpolator` and
concrete implementations (`IDWInterpolator`, `KrigingInterpolator`,
`RBFInterpolator`, `LinearInterpolator`, `CubicInterpolator`) plus an
`InterpolationManager` facade.

## Next Steps

1. See the [MATH module page](../../../GEO-INFER-INTRA/docs/modules/geo-infer-math.md)
   in the INTRA documentation hub for the full capability overview.
2. Run the runnable examples under `GEO-INFER-MATH/examples/`:

```
```bash
uv run python GEO-INFER-MATH/examples/spatial_statistics_example.py
uv run python GEO-INFER-MATH/examples/advanced_geospatial_analysis.py
```

3. Explore the module source under `GEO-INFER-MATH/src/geo_infer_math/` for
   the reference documentation of each subpackage.
