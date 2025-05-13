"""
Statistical and machine learning models for geospatial data.

This package provides specialized mathematical models designed specifically
for analyzing geographical and spatial patterns and relationships.
"""

from geo_infer_math.models.regression import *
from geo_infer_math.models.clustering import *
from geo_infer_math.models.dimension_reduction import *
from geo_infer_math.models.manifold_learning import *
from geo_infer_math.models.spectral_analysis import *

__all__ = [
    "regression",
    "clustering",
    "dimension_reduction",
    "manifold_learning",
    "spectral_analysis"
]
