"""
GEO-INFER-ACT: Active Inference modeling module for GEO-INFER framework.

This module provides mathematical and computational tools for modeling complex
ecological and civic systems using principles from active inference theory.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"
__email__ = "blanket@activeinference.institute"

# Import core classes and functions
try:
    from .core.active_inference import ActiveInferenceModel
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
        'ActiveInferenceModel',
        'FreeEnergyCalculator', 
        'GenerativeModel',
        'BayesianBeliefUpdate',
        'PolicySelector',
        'VariationalInference',
        'DynamicCausalModel',
        'SpatialActiveInferenceAgent',
        'ClimateModel',
        'IntegrationUtils',
    ]
except ImportError as e:
    # If imports fail, provide a minimal interface
    __all__ = []
    import logging
    logging.warning(f"Some ACT module components not available: {e}") 