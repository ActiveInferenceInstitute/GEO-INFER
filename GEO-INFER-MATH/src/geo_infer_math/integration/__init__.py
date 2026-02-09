"""
Module Integration Layer

This package provides deep integration layers for connecting
GEO-INFER-MATH with other GEO-INFER modules (AI, ACT, BAYES).
"""

from geo_infer_math.integration.ai import *
from geo_infer_math.integration.act import *
from geo_infer_math.integration.bayes import *

__all__ = [
    # AI Integration
    "AIGradientHelpers",
    "SpatialLossFunctions",
    "OptimizationBridges",
    "SpatialTensorOperations",
    "SpatialAttention",
    # ACT Integration
    "FreeEnergyCalculator",
    "VariationalInferenceHelpers",
    "BeliefUpdating",
    "PolicyOptimization",
    "GenerativeModels",
    # BAYES Integration
    "PosteriorHelpers",
    "PriorBuilders",
    "MCMCHelpers",
    "BayesianOptimization",
    "ModelSelection",
]

