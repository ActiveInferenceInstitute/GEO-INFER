"""
Visualization tools for GEO-INFER-SPM

This module provides visualization functions for creating statistical
parametric maps, diagnostic plots, and interactive visualizations
of SPM analysis results.
"""

from .maps import (
    create_statistical_map,
    plot_spm_results,
    _plot_beta_coefficients,
    _plot_residuals,
    _plot_model_diagnostics,
    create_interactive_map
)
from .diagnostics import (
    plot_model_diagnostics,
    plot_contrast_results,
    _plot_qq_residuals,
    _plot_residuals_vs_fitted,
    _plot_scale_location,
    _plot_residual_histogram,
    _plot_cooks_distance,
    _plot_leverage,
    _compute_diagnostic_stats
)
from .interactive import (
    create_interactive_map,
    create_dashboard,
    create_time_series_explorer
)

__all__ = [
    # Main visualization functions
    "create_statistical_map",
    "plot_spm_results",
    "plot_model_diagnostics",
    "plot_contrast_results",
    "create_interactive_map",
    "create_dashboard",
    "create_time_series_explorer",

    # Internal helper functions (for advanced users)
    "_plot_beta_coefficients",
    "_plot_residuals",
    "_plot_model_diagnostics",
    "_plot_qq_residuals",
    "_plot_residuals_vs_fitted",
    "_plot_scale_location",
    "_plot_residual_histogram",
    "_plot_cooks_distance",
    "_plot_leverage",
    "_compute_diagnostic_stats"
]
