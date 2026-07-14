"""
Utility functions for GEO-INFER-ACT.

This module provides helper functions and utilities for
configuration, computation, visualization, and integration.
"""

from geo_infer_act.utils.config import load_config, save_config
from geo_infer_act.utils.math import (
    categorical_posterior,
    entropy,
    kl_divergence,
    normalize_distribution,
    precision_weighted_error,
    sample_dirichlet,
)
from geo_infer_act.utils.visualization import (
    plot_belief_update,
    plot_free_energy,
    plot_policies,
)
from geo_infer_act.utils.integration import (
    integrate_space,
    integrate_time,
    integrate_sim,
)
from geo_infer_act.utils.spatial_diagnostics import SpatialDiagnostics

__all__ = [
    "load_config",
    "save_config",
    "categorical_posterior",
    "entropy",
    "kl_divergence",
    "normalize_distribution",
    "precision_weighted_error",
    "sample_dirichlet",
    "plot_belief_update",
    "plot_free_energy",
    "plot_policies",
    "integrate_space",
    "integrate_time",
    "integrate_sim",
    "SpatialDiagnostics",
]
