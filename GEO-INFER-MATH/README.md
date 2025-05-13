# GEO-INFER-MATH

A comprehensive mathematical library for geospatial data analysis and inference. This module provides specialized mathematical tools, models, and algorithms optimized for processing and analyzing geographical and spatial data.

## Features

- **Spatial Statistics**: Tools for analyzing spatial patterns, autocorrelation, and distributions
- **Geometric Operations**: Functions for distances, areas, intersections, and other geometric properties
- **Interpolation Methods**: Techniques for spatial interpolation and extrapolation
- **Optimization Algorithms**: Specialized algorithms for geospatial optimization problems
- **Differential Equations**: Tools for solving differential equations in geospatial contexts
- **Tensor Operations**: Functions for multi-dimensional geospatial data analysis
- **Coordinate Transformations**: Tools for projection and coordinate system transformations
- **Regression Models**: Specialized regression techniques for spatial data
- **Clustering Methods**: Algorithms for spatial clustering and regionalization
- **Dimension Reduction**: Techniques for reducing dimensionality of spatial data

## Installation

```bash
pip install geo-infer-math
```

For development installation:

```bash
git clone https://github.com/geo-infer/geo-infer-math.git
cd geo-infer-math
pip install -e ".[dev]"
```

## Quick Start

```python
import numpy as np
from geo_infer_math.core.geometry import haversine_distance
from geo_infer_math.core.spatial_statistics import MoranI

# Calculate distance between two points on Earth
distance = haversine_distance(
    lat1=40.7128,  # New York
    lon1=-74.0060,
    lat2=34.0522,  # Los Angeles
    lon2=-118.2437
)
print(f"Distance between New York and Los Angeles: {distance:.2f} km")

# Calculate Moran's I spatial autocorrelation
values = np.array([45, 50, 55, 70, 65, 60, 50, 55, 60, 65])
coords = np.array([
    [0, 0], [1, 0], [2, 0], [3, 0], [4, 0],
    [0, 1], [1, 1], [2, 1], [3, 1], [4, 1]
])
moran = MoranI()
result = moran.compute(values, coords)
print(f"Moran's I: {result['I']:.4f} (p-value: {result['p_value']:.4f})")
```

## Module Structure

The library is organized into several submodules:

- `geo_infer_math.core`: Core mathematical operations and algorithms
  - `spatial_statistics`: Functions for analyzing spatial patterns
  - `interpolation`: Methods for spatial interpolation
  - `optimization`: Algorithms for geospatial optimization
  - `differential`: Tools for differential equations
  - `tensors`: Operations for multi-dimensional data
  - `geometry`: Functions for geometric calculations
  - `transforms`: Coordinate transformations
- `geo_infer_math.models`: Statistical and machine learning models
  - `regression`: Spatial regression models
  - `clustering`: Spatial clustering methods
  - `dimension_reduction`: Dimensionality reduction techniques
  - `manifold_learning`: Methods for manifold learning
  - `spectral_analysis`: Spectral decomposition methods
- `geo_infer_math.utils`: Utility functions and helpers
- `geo_infer_math.api`: Clean API interfaces for accessing functionality

## Documentation

Full documentation is available at [https://geo-infer-math.readthedocs.io/](https://geo-infer-math.readthedocs.io/)

## Examples

Check the `examples/` directory for more detailed examples:

- Basic spatial statistics
- Geometric calculations and transformations
- Advanced spatial modeling
- Optimization techniques
- Dimension reduction for spatial data

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- GEO-INFER project team
- Contributors to spatial statistics and mathematical geospatial methods 