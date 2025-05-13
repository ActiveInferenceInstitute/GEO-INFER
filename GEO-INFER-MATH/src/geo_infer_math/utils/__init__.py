"""
Utility functions and tools for mathematical operations in geospatial context.

This package provides helper functions, data conversion tools, and other utilities
that support the core mathematical operations and models.
"""

from geo_infer_math.utils.validation import validate_coordinates, validate_matrix
from geo_infer_math.utils.conversion import degrees_to_radians, radians_to_degrees
from geo_infer_math.utils.constants import EARTH_RADIUS_KM, WGS84_PARAMETERS
from geo_infer_math.utils.decorators import memoize, validate_input
from geo_infer_math.utils.parallel import parallel_compute

__all__ = [
    # Validation utilities
    "validate_coordinates", "validate_matrix",
    
    # Conversion utilities
    "degrees_to_radians", "radians_to_degrees",
    
    # Constants
    "EARTH_RADIUS_KM", "WGS84_PARAMETERS",
    
    # Decorators
    "memoize", "validate_input",
    
    # Parallel computation
    "parallel_compute"
]
