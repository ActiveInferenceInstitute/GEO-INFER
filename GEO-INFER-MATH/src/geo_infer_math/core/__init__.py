"""
Core mathematical components for geospatial analysis.

This package provides fundamental mathematical operations and algorithms
that serve as building blocks for more complex geospatial analysis.
"""

# Import available modules
from geo_infer_math.core.spatial_statistics import *
from geo_infer_math.core.interpolation import *
from geo_infer_math.core.optimization import *
from geo_infer_math.core.geometry import *

# Import newly implemented modules
try:
    from geo_infer_math.core.numerical_methods import *
    _numerical_methods_available = True
except ImportError:
    _numerical_methods_available = False

try:
    from geo_infer_math.core.linalg_tensor import *
    _linalg_tensor_available = True
except ImportError:
    _linalg_tensor_available = False

try:
    from geo_infer_math.core.transforms import *
    _transforms_available = True
except ImportError:
    _transforms_available = False

try:
    from geo_infer_math.core.graph_theory import *
    _graph_theory_available = True
except ImportError:
    _graph_theory_available = False

# Build __all__ list based on available modules
__all__ = [
    "spatial_statistics",
    "interpolation",
    "optimization",
    "geometry"
]

if _numerical_methods_available:
    __all__.append("numerical_methods")

if _linalg_tensor_available:
    __all__.append("linalg_tensor")

if _transforms_available:
    __all__.append("transforms")

if _graph_theory_available:
    __all__.append("graph_theory")
