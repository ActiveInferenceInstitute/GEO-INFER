"""
Statistical map visualization for GEO-INFER-SPM

This module provides functions for creating statistical parametric maps
and visualizing SPM analysis results as spatial plots and maps.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import warnings

try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.patches import Circle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("matplotlib not available. Visualization functions limited.")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..models.data_models import SPMResult, ContrastResult


def create_statistical_map(spm_result: SPMResult, contrast_idx: int = 0,
                          threshold: Optional[float] = None,
                          colormap: str = 'RdBu_r',
                          title: Optional[str] = None) -> Dict[str, Any]:
    """
    Create statistical parametric map visualization.

    Args:
        spm_result: SPM analysis results
        contrast_idx: Index of contrast to visualize
        threshold: Statistical threshold for significance
        colormap: Colormap name
        title: Plot title

    Returns:
        Dictionary with visualization data
    """
    if contrast_idx >= len(spm_result.contrasts):
        raise ValueError(f"Contrast index {contrast_idx} out of range")

    contrast = spm_result.contrasts[contrast_idx]

    # Get statistical values
    if hasattr(contrast, 't_statistic') and contrast.t_statistic.ndim == 1:
        stat_values = contrast.t_statistic
    else:
        # For multi-dimensional data, use first component
        stat_values = contrast.t_statistic.flatten()

    coordinates = spm_result.spm_data.coordinates

    # Apply threshold
    if threshold is None:
        threshold = contrast.threshold if hasattr(contrast, 'threshold') else 0.05

    significant_mask = None
    if hasattr(contrast, 'significance_mask') and contrast.significance_mask is not None:
        significant_mask = contrast.significance_mask
    else:
        # Compute based on threshold
        p_values = contrast.p_values if hasattr(contrast, 'p_values') else np.ones_like(stat_values)
        significant_mask = p_values < threshold

    # Create visualization data
    viz_data = {
        'coordinates': coordinates.tolist(),
        'stat_values': stat_values.tolist(),
        'significant_mask': significant_mask.tolist() if significant_mask is not None else None,
        'threshold': threshold,
        'colormap': colormap,
        'title': title or f"SPM Contrast {contrast_idx}",
        'contrast_name': getattr(contrast, 'name', f'Contrast {contrast_idx}'),
        'correction_method': getattr(contrast, 'correction_method', 'uncorrected')
    }

    # Create matplotlib figure if available
    if MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # Create scatter plot colored by statistic
        sc = ax.scatter(coordinates[:, 0], coordinates[:, 1],
                       c=stat_values, cmap=colormap,
                       s=50, alpha=0.7, edgecolors='black', linewidth=0.5)

        # Highlight significant points
        if significant_mask is not None and np.any(significant_mask):
            sig_coords = coordinates[significant_mask]
            ax.scatter(sig_coords[:, 0], sig_coords[:, 1],
                      c='red', s=60, marker='*', label='Significant')

        # Add colorbar
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('T-statistic')

        # Set labels and title
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title(viz_data['title'])
        ax.grid(True, alpha=0.3)

        # Add legend if significant points exist
        if significant_mask is not None and np.any(significant_mask):
            ax.legend()

        plt.tight_layout()

        viz_data['matplotlib_figure'] = fig

    return viz_data


def plot_spm_results(spm_result: SPMResult, plot_type: str = 'stat_map',
                    **kwargs) -> Dict[str, Any]:
    """
    Create comprehensive SPM results visualization.

    Args:
        spm_result: SPM analysis results
        plot_type: Type of plot ('stat_map', 'beta_map', 'residuals', 'diagnostics')
        **kwargs: Additional plotting parameters

    Returns:
        Dictionary with visualization data
    """
    if not MATPLOTLIB_AVAILABLE:
        return {'error': 'matplotlib not available for plotting'}

    if plot_type == 'stat_map':
        return create_statistical_map(spm_result, **kwargs)

    elif plot_type == 'beta_map':
        # Visualize regression coefficients
        return _plot_beta_coefficients(spm_result, **kwargs)

    elif plot_type == 'residuals':
        # Visualize model residuals
        return _plot_residuals(spm_result, **kwargs)

    elif plot_type == 'diagnostics':
        # Model diagnostic plots
        return _plot_model_diagnostics(spm_result, **kwargs)

    else:
        raise ValueError(f"Unknown plot type: {plot_type}")


def _plot_beta_coefficients(spm_result: SPMResult, **kwargs) -> Dict[str, Any]:
    """Plot regression coefficient maps."""
    beta = spm_result.beta_coefficients
    coordinates = spm_result.spm_data.coordinates

    if beta.ndim == 1:
        # Single coefficient set
        fig, ax = plt.subplots(figsize=(8, 6))
        sc = ax.scatter(coordinates[:, 0], coordinates[:, 1],
                       c=beta, cmap='viridis', s=50, alpha=0.7)
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Coefficient Value')
        ax.set_title('Regression Coefficients')
    else:
        # Multiple coefficients - create subplots
        n_coeffs = min(beta.shape[0], 9)  # Limit to 9 subplots
        n_cols = int(np.ceil(np.sqrt(n_coeffs)))
        n_rows = int(np.ceil(n_coeffs / n_cols))

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 4*n_rows))
        if n_coeffs == 1:
            axes = [axes]

        axes = axes.flatten()

        for i in range(n_coeffs):
            ax = axes[i]
            sc = ax.scatter(coordinates[:, 0], coordinates[:, 1],
                           c=beta[i], cmap='viridis', s=30, alpha=0.7)
            ax.set_title(f'β{i}')
            plt.colorbar(sc, ax=ax)

        # Hide unused subplots
        for i in range(n_coeffs, len(axes)):
            axes[i].set_visible(False)

    plt.tight_layout()

    return {
        'plot_type': 'beta_coefficients',
        'matplotlib_figure': fig
    }


def _plot_residuals(spm_result: SPMResult, **kwargs) -> Dict[str, Any]:
    """Plot model residuals."""
    residuals = spm_result.residuals
    coordinates = spm_result.spm_data.coordinates

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Spatial distribution of residuals
    sc = ax1.scatter(coordinates[:, 0], coordinates[:, 1],
                    c=residuals, cmap='RdYlBu_r', s=50, alpha=0.7)
    ax1.set_title('Residual Spatial Distribution')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    cbar1 = plt.colorbar(sc, ax=ax1)
    cbar1.set_label('Residual Value')

    # Residual histogram
    ax2.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
    ax2.set_title('Residual Distribution')
    ax2.set_xlabel('Residual Value')
    ax2.set_ylabel('Frequency')

    # Add normality test
    from scipy import stats
    _, p_value = stats.shapiro(residuals)
    ax2.text(0.05, 0.95, f'Shapiro-Wilk p = {p_value:.3f}',
            transform=ax2.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()

    return {
        'plot_type': 'residuals',
        'matplotlib_figure': fig,
        'shapiro_p_value': p_value
    }


def _plot_model_diagnostics(spm_result: SPMResult, **kwargs) -> Dict[str, Any]:
    """Create model diagnostic plots."""
    diagnostics = spm_result.model_diagnostics

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Q-Q plot for residuals
    ax1 = axes[0, 0]
    residuals = spm_result.residuals
    stats.probplot(residuals, dist="norm", plot=ax1)
    ax1.set_title('Normal Q-Q Plot')

    # 2. Residuals vs Fitted
    ax2 = axes[0, 1]
    fitted = spm_result.spm_data.data - residuals
    ax2.scatter(fitted, residuals, alpha=0.6)
    ax2.axhline(y=0, color='red', linestyle='--')
    ax2.set_xlabel('Fitted Values')
    ax2.set_ylabel('Residuals')
    ax2.set_title('Residuals vs Fitted')

    # 3. Scale-Location plot
    ax3 = axes[1, 0]
    sqrt_abs_residuals = np.sqrt(np.abs(residuals))
    ax3.scatter(fitted, sqrt_abs_residuals, alpha=0.6)
    ax3.set_xlabel('Fitted Values')
    ax3.set_ylabel('√|Residuals|')
    ax3.set_title('Scale-Location Plot')

    # 4. Cook's distance (simplified)
    ax4 = axes[1, 1]
    # Simplified Cook's distance calculation
    n = len(residuals)
    p = spm_result.design_matrix.n_regressors
    mse = np.sum(residuals**2) / (n - p)
    leverage = np.diag(np.linalg.pinv(spm_result.design_matrix.matrix.T @
                                    spm_result.design_matrix.matrix) @
                      spm_result.design_matrix.matrix.T @
                      spm_result.design_matrix.matrix)

    cooks_d = (residuals**2 / (p * mse)) * (leverage / (1 - leverage)**2)

    ax4.scatter(range(len(cooks_d)), cooks_d, alpha=0.6)
    ax4.axhline(y=4/n, color='red', linestyle='--', label='4/n threshold')
    ax4.set_xlabel('Observation Index')
    ax4.set_ylabel("Cook's Distance")
    ax4.set_title("Cook's Distance")
    ax4.legend()

    plt.tight_layout()

    return {
        'plot_type': 'diagnostics',
        'matplotlib_figure': fig,
        'diagnostic_stats': {
            'r_squared': diagnostics.get('r_squared'),
            'adjusted_r_squared': diagnostics.get('adjusted_r_squared'),
            'f_statistic': diagnostics.get('f_statistic'),
            'max_cooks_d': np.max(cooks_d)
        }
    }


def create_interactive_map(spm_result: SPMResult, contrast_idx: int = 0,
                          **kwargs) -> Optional[Any]:
    """
    Create interactive statistical map using plotly.

    Args:
        spm_result: SPM analysis results
        contrast_idx: Index of contrast to visualize
        **kwargs: Additional plotting parameters

    Returns:
        Plotly figure object or None if plotly not available
    """
    if not PLOTLY_AVAILABLE:
        warnings.warn("plotly not available. Cannot create interactive map.")
        return None

    if contrast_idx >= len(spm_result.contrasts):
        raise ValueError(f"Contrast index {contrast_idx} out of range")

    contrast = spm_result.contrasts[contrast_idx]
    coordinates = spm_result.spm_data.coordinates

    # Get statistical values
    stat_values = contrast.t_statistic.flatten() if contrast.t_statistic.ndim > 1 else contrast.t_statistic

    # Create hover text
    hover_text = []
    for i in range(len(coordinates)):
        hover_text.append(
            f"Longitude: {coordinates[i, 0]:.4f}<br>"
            f"Latitude: {coordinates[i, 1]:.4f}<br>"
            f"T-statistic: {stat_values[i]:.3f}<br>"
            f"P-value: {contrast.p_values[i]:.3f}"
        )

    # Determine colors based on significance
    if hasattr(contrast, 'significance_mask') and contrast.significance_mask is not None:
        colors = ['red' if sig else 'blue' for sig in contrast.significance_mask]
        color_label = 'Significant'
    else:
        colors = stat_values
        color_label = 'T-statistic'

    # Create scatter plot
    fig = go.Figure(data=go.Scattergeo(
        lon=coordinates[:, 0],
        lat=coordinates[:, 1],
        text=hover_text,
        mode='markers',
        marker=dict(
            size=8,
            color=colors,
            colorscale='RdBu_r' if isinstance(colors[0], (int, float)) else None,
            showscale=True if isinstance(colors[0], (int, float)) else False,
            colorbar=dict(title=color_label) if isinstance(colors[0], (int, float)) else None,
            line=dict(width=1, color='black')
        ),
        hovertemplate="%{text}<extra></extra>"
    ))

    # Update layout
    fig.update_layout(
        title=f"SPM Statistical Map - {getattr(contrast, 'name', f'Contrast {contrast_idx}')}",
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=600
    )

    return fig
