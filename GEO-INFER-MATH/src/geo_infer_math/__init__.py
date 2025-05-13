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

from geo_infer_math.core import (
    spatial_statistics, interpolation, optimization, 
    differential, tensors, geometry, transforms
)
from geo_infer_math.models import (
    regression, clustering, dimension_reduction,
    manifold_learning, spectral_analysis
)

__all__ = [
    # Core mathematical modules
    "spatial_statistics", "interpolation", "optimization",
    "differential", "tensors", "geometry", "transforms",
    
    # Statistical and machine learning models
    "regression", "clustering", "dimension_reduction",
    "manifold_learning", "spectral_analysis"
]
