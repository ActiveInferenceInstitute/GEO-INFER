"""
API interfaces for GEO-INFER-MATH functionality.

This package provides clean, consistent interfaces for accessing the
mathematical operations and models provided by GEO-INFER-MATH.
"""

from geo_infer_math.api.spatial_analysis import SpatialAnalysisAPI
from geo_infer_math.api.geometric_operations import GeometricOperationsAPI
from geo_infer_math.api.statistical_modeling import StatisticalModelingAPI
from geo_infer_math.api.optimization import OptimizationAPI
from geo_infer_math.api.coordinate_management import CoordinateManagementAPI

# Import convenience modules
try:
    from geo_infer_math.api.convenience import *
    _convenience_available = True
except ImportError:
    _convenience_available = False

__all__ = [
    "SpatialAnalysisAPI",
    "GeometricOperationsAPI",
    "StatisticalModelingAPI",
    "OptimizationAPI",
    "CoordinateManagementAPI"
]

if _convenience_available:
    __all__.extend([
        "ActiveInferenceConvenience",
        "BayesianConvenience",
        "AIConvenience",
        "InformationTheoryConvenience",
        "SpatialConvenience",
        "IntegrationConvenience",
    ])
