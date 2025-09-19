"""
Core SPM functionality

This module contains the core algorithms and methods for Statistical Parametric Mapping,
including General Linear Model fitting, Random Field Theory, contrast analysis,
and spatial-temporal statistical inference.
"""

from .glm import GeneralLinearModel, fit_glm
from .rft import RandomFieldTheory, compute_spm
from .contrasts import Contrast, contrast
from .spatial_analysis import SpatialAnalyzer
from .temporal_analysis import TemporalAnalyzer
from .bayesian import BayesianSPM

__all__ = [
    "GeneralLinearModel",
    "fit_glm",
    "RandomFieldTheory",
    "compute_spm",
    "Contrast",
    "contrast",
    "SpatialAnalyzer",
    "TemporalAnalyzer",
    "BayesianSPM"
]
