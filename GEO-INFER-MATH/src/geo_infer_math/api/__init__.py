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

__all__ = [
    "SpatialAnalysisAPI",
    "GeometricOperationsAPI",
    "StatisticalModelingAPI",
    "OptimizationAPI",
    "CoordinateManagementAPI"
]
