"""
Advanced statistical modeling for GEO-INFER-SPM

This module provides advanced statistical methods for geospatial analysis,
including mixed effects models, non-parametric methods, model validation,
and sophisticated inference techniques.
"""

from .mixed_effects import MixedEffectsSPM
from .nonparametric import NonparametricSPM
from .model_validation import ModelValidator
from .spatial_regression import SpatialRegression

__all__ = [
    "MixedEffectsSPM",
    "NonparametricSPM",
    "ModelValidator",
    "SpatialRegression"
]
