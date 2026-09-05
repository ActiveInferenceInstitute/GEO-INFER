"""
Visualization tools for GEO-INFER-SPM

This module provides visualization functions for creating statistical
parametric maps, diagnostic plots, and interactive visualizations
of SPM analysis results.
"""

from .maps import create_statistical_map, plot_spm_results
from .diagnostics import plot_model_diagnostics, plot_contrast_results
from .interactive import (
    create_interactive_map,
    create_dashboard,
    create_time_series_explorer,
)

__all__ = [
    "create_statistical_map",
    "plot_spm_results",
    "plot_model_diagnostics",
    "plot_contrast_results",
    "create_interactive_map",
    "create_dashboard",
    "create_time_series_explorer",
]
