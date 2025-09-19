"""
GEO-INFER-MATH

A comprehensive mathematical library for geospatial data analysis and inference.
This module provides specialized mathematical tools, models, and algorithms that
are optimized for processing and analyzing geographical and spatial data.

Key components:
- Spatial statistics and probability distributions
- Geospatial optimization algorithms
- Spatial interpolation and extrapolation methods
- Vector and raster math operations
- Coordinate transformations and projections
- Geometric operations and calculations
- Tensor operations for multi-dimensional geospatial data
"""

# Import available core modules
from geo_infer_math.core.spatial_statistics import *
from geo_infer_math.core.interpolation import *
from geo_infer_math.core.optimization import *
from geo_infer_math.core.geometry import *

# Try to import newly implemented modules
_available_core = []
_available_models = []

try:
    from geo_infer_math.core.numerical_methods import *
    _available_core.append("numerical_methods")
except ImportError:
    pass

try:
    from geo_infer_math.core.linalg_tensor import *
    _available_core.append("linalg_tensor")
except ImportError:
    pass

try:
    from geo_infer_math.core.transforms import *
    _available_core.append("transforms")
except ImportError:
    pass

try:
    from geo_infer_math.core.graph_theory import *
    _available_core.append("graph_theory")
except ImportError:
    pass

# Try to import model modules
try:
    from geo_infer_math.models.regression import *
    _available_models.append("regression")
except ImportError:
    pass

try:
    from geo_infer_math.models.clustering import *
    _available_models.append("clustering")
except ImportError:
    pass

# Build __all__ list
__all__ = [
    # Core mathematical modules
    "spatial_statistics", "interpolation", "optimization", "geometry"
] + _available_core + _available_models
