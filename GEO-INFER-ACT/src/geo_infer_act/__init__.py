"""
GEO-INFER-ACT: Active Inference modeling module for GEO-INFER framework.

This module provides mathematical and computational tools for modeling complex
ecological and civic systems using principles from active inference theory.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"
__email__ = "blanket@activeinference.institute"

from .core.active_inference import ActiveInferenceModel
from .core.types import (
    ActiveInferenceStepResult,
    FreeEnergyBreakdown,
    H3BeliefUpdateResult,
    H3GridInferenceResult,
    H3SpatialConsistency,
    PolicyEvaluation,
)
from .core.free_energy import FreeEnergyCalculator
from .core.generative_model import GenerativeModel
from .core.belief_updating import BayesianBeliefUpdate
from .core.policy_selection import PolicySelector
from .core.variational_inference import VariationalInference
from .core.dynamic_causal_model import DynamicCausalModel
from .core.spatial_agent import SpatialActiveInferenceAgent
from .models.climate import ClimateModel
from .utils.integration import IntegrationUtils

__all__ = [
    "ActiveInferenceModel",
    "ActiveInferenceStepResult",
    "FreeEnergyBreakdown",
    "H3BeliefUpdateResult",
    "H3GridInferenceResult",
    "H3SpatialConsistency",
    "PolicyEvaluation",
    "FreeEnergyCalculator",
    "GenerativeModel",
    "BayesianBeliefUpdate",
    "PolicySelector",
    "VariationalInference",
    "DynamicCausalModel",
    "SpatialActiveInferenceAgent",
    "ClimateModel",
    "IntegrationUtils",
]
