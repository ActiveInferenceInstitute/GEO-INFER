"""
API interfaces for GEO-INFER-MATH functionality.

This package provides clean, consistent interfaces for accessing the
mathematical operations and models provided by GEO-INFER-MATH.
"""

from geo_infer_math.api.spatial_analysis import SpatialAnalysisAPI

# Optional API modules (may not be implemented yet)
_available_apis = ["SpatialAnalysisAPI"]

try:
    from geo_infer_math.api.geometric_operations import GeometricOperationsAPI
    _available_apis.append("GeometricOperationsAPI")
except ImportError:
    pass

try:
    from geo_infer_math.api.statistical_modeling import StatisticalModelingAPI
    _available_apis.append("StatisticalModelingAPI")
except ImportError:
    pass

try:
    from geo_infer_math.api.optimization import OptimizationAPI
    _available_apis.append("OptimizationAPI")
except ImportError:
    pass

try:
    from geo_infer_math.api.coordinate_management import CoordinateManagementAPI
    _available_apis.append("CoordinateManagementAPI")
except ImportError:
    pass

# Import convenience modules
try:
    from geo_infer_math.api.convenience import *
    _convenience_available = True
except ImportError:
    _convenience_available = False

__all__ = list(_available_apis)

if _convenience_available:
    __all__.extend([
        "ActiveInferenceConvenience",
        "BayesianConvenience",
        "AIConvenience",
        "InformationTheoryConvenience",
        "SpatialConvenience",
        "IntegrationConvenience",
    ])
