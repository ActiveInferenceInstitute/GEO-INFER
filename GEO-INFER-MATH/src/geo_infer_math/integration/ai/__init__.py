"""
AI Module Integration

This module provides deep integration with GEO-INFER-AI,
including gradient helpers, loss functions, and tensor operations.
"""

from geo_infer_math.integration.ai.gradient_helpers import AIGradientHelpers
from geo_infer_math.integration.ai.loss_functions import SpatialLossFunctions
from geo_infer_math.integration.ai.optimization_bridges import OptimizationBridges
from geo_infer_math.integration.ai.tensor_operations import TensorOperations
from geo_infer_math.integration.ai.spatial_attention import SpatialAttention

__all__ = [
    "AIGradientHelpers",
    "SpatialLossFunctions",
    "OptimizationBridges",
    "TensorOperations",
    "SpatialAttention",
]

