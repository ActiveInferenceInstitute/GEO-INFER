"""
Interactive visualization tools for GEO-INFER-SPM

This module provides interactive visualization capabilities using
web-based plotting libraries for exploratory data analysis and
result presentation.
"""

from typing import Dict, List, Optional, Any
import warnings

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..models.data_models import SPMResult, ContrastResult


def create_interactive_map(spm_result: SPMResult, contrast_idx: int = 0,
                          map_type: str = 'scattergeo', **kwargs) -> Optional[Any]:
    """
    Create interactive geographical map of SPM results.

    Args:
        spm_result: SPM analysis results
        contrast_idx: Index of contrast to visualize
        map_type: Type of map ('scattergeo', 'choropleth')
        **kwargs: Additional plotting parameters

    Returns:
        Plotly figure object or None if plotly not available
    """
    if not PLOTLY_AVAILABLE:
        warnings.warn("plotly not available for interactive visualization")
        return None

    if contrast_idx >= len(spm_result.contrasts):
        raise ValueError(f"Contrast index {contrast_idx} out of range")

    contrast = spm_result.contrasts[contrast_idx]
    coordinates = spm_result.spm_data.coordinates

    # Prepare data
    stat_values = (contrast.t_statistic.flatten() if contrast.t_statistic.ndim > 1
                  else contrast.t_statistic)

    # Create hover information
    hover_text = []
    for i in range(len(coordinates)):
        sig_status = "Significant" if (hasattr(contrast, 'significance_mask') and
                                     contrast.significance_mask is not None and
                                     contrast.significance_mask[i]) else "Not significant"

        hover_text.append(
            f"Point {i}<br>"
            f"Longitude: {coordinates[i, 0]:.4f}<br>"
            f"Latitude: {coordinates[i, 1]:.4f}<br>"
            f"T-statistic: {stat_values[i]:.3f}<br>"
            f"P-value: {contrast.p_values[i]:.3f}<br>"
            f"Status: {sig_status}"
        )

    if map_type == 'scattergeo':
        # Create scatter geo plot
        fig = go.Figure(data=go.Scattergeo(
            lon=coordinates[:, 0],
            lat=coordinates[:, 1],
            text=hover_text,
            mode='markers',
            marker=dict(
                size=8,
                color=stat_values,
                colorscale='RdBu_r',
                showscale=True,
                colorbar=dict(title='T-statistic'),
                line=dict(width=1, color='black'),
                # Highlight significant points
                symbol='star' if (hasattr(contrast, 'significance_mask') and
                                contrast.significance_mask is not None and
                                np.any(contrast.significance_mask)) else 'circle'
            ),
            hovertemplate="%{text}<extra></extra>"
        ))

        # Update layout for geographical projection
        fig.update_layout(
            title=f"SPM Statistical Map - {getattr(contrast, 'name', f'Contrast {contrast_idx}')}",
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="RebeccaPurple",
                projection_type='natural earth',
                showland=True,
                landcolor="LightGreen",
                showocean=True,
                oceancolor="LightBlue"
            ),
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )

    elif map_type == 'choropleth':
        # For choropleth, we would need polygon data
        # This is a placeholder for future implementation
        warnings.warn("Choropleth map requires polygon data. Using scatter plot instead.")
        return create_interactive_map(spm_result, contrast_idx, 'scattergeo', **kwargs)

    else:
        raise ValueError(f"Unknown map type: {map_type}")

    return fig


def create_dashboard(spm_result: SPMResult, include_diagnostics: bool = True) -> Optional[Any]:
    """
    Create comprehensive interactive dashboard of SPM results.

    Args:
        spm_result: SPM analysis results
        include_diagnostics: Whether to include diagnostic plots

    Returns:
        Plotly figure with dashboard or None if plotly not available
    """
    if not PLOTLY_AVAILABLE:
        warnings.warn("plotly not available for dashboard creation")
        return None

    # Create subplot figure
    n_rows = 2 if include_diagnostics else 1
    n_cols = 3

    subplot_titles = []
    if spm_result.contrasts:
        subplot_titles.append("Statistical Map")
        subplot_titles.append("T-Statistic Distribution")
        subplot_titles.append("P-Value Distribution")

    if include_diagnostics:
        subplot_titles.extend([
            "Residuals vs Fitted",
            "Q-Q Plot",
            "Cook's Distance"
        ])

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=subplot_titles,
        specs=[[{"type": "scattergeo"}, {"type": "histogram"}, {"type": "histogram"}],
               [{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}] if include_diagnostics else []]
    )

    # Add statistical map
    if spm_result.contrasts:
        contrast = spm_result.contrasts[0]  # Use first contrast
        coordinates = spm_result.spm_data.coordinates
        stat_values = contrast.t_statistic.flatten()

        fig.add_trace(
            go.Scattergeo(
                lon=coordinates[:, 0],
                lat=coordinates[:, 1],
                mode='markers',
                marker=dict(
                    size=6,
                    color=stat_values,
                    colorscale='RdBu_r',
                    showscale=True,
                    colorbar=dict(title='T-statistic', x=0.25)
                ),
                showlegend=False
            ),
            row=1, col=1
        )

        # T-statistic histogram
        fig.add_trace(
            go.Histogram(x=stat_values, nbinsx=30, showlegend=False),
            row=1, col=2
        )

        # P-value histogram
        fig.add_trace(
            go.Histogram(x=contrast.p_values, nbinsx=30, showlegend=False),
            row=1, col=3
        )

    # Add diagnostic plots
    if include_diagnostics:
        residuals = spm_result.residuals
        fitted = spm_result.spm_data.data - residuals

        # Residuals vs Fitted
        fig.add_trace(
            go.Scatter(x=fitted, y=residuals, mode='markers',
                      marker=dict(size=4, opacity=0.6), showlegend=False),
            row=2, col=1
        )

        # Q-Q plot
        from scipy import stats
        (osm, osr), (slope, intercept, r) = stats.probplot(residuals, dist="norm")
        fig.add_trace(
            go.Scatter(x=osm, y=osr, mode='markers',
                      marker=dict(size=4, opacity=0.6), showlegend=False),
            row=2, col=2
        )
        # Add reference line
        fig.add_trace(
            go.Scatter(x=osm, y=slope*osm + intercept, mode='lines',
                      line=dict(color='red', dash='dash'), showlegend=False),
            row=2, col=2
        )

        # Cook's distance (simplified)
        n, p = spm_result.design_matrix.matrix.shape
        mse = np.sum(residuals**2) / (n - p)
        hat_matrix = (spm_result.design_matrix.matrix @
                     np.linalg.pinv(spm_result.design_matrix.matrix.T @
                                  spm_result.design_matrix.matrix) @
                     spm_result.design_matrix.matrix.T)
        leverage = np.diag(hat_matrix)
        cooks_d = (residuals**2 / (p * mse)) * (leverage / (1 - leverage)**2)

        fig.add_trace(
            go.Scatter(x=list(range(len(cooks_d))), y=cooks_d, mode='markers',
                      marker=dict(size=4, opacity=0.6), showlegend=False),
            row=2, col=3
        )

    # Update layout
    fig.update_layout(
        height=800,
        title_text="SPM Analysis Dashboard",
        showlegend=False
    )

    # Update geo subplot
    fig.update_geos(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth'
    )

    return fig


def create_time_series_explorer(spm_result: SPMResult) -> Optional[Any]:
    """
    Create interactive time series explorer for temporal SPM data.

    Args:
        spm_result: SPM analysis results with temporal dimension

    Returns:
        Plotly figure for time series exploration or None
    """
    if not PLOTLY_AVAILABLE:
        warnings.warn("plotly not available for time series explorer")
        return None

    if not spm_result.spm_data.has_temporal:
        warnings.warn("No temporal data available for time series explorer")
        return None

    # This would create interactive time series plots
    # Implementation depends on specific temporal data structure
    # Placeholder for now

    fig = go.Figure()

    fig.update_layout(
        title="Time Series Explorer (Under Development)",
        xaxis_title="Time",
        yaxis_title="Value"
    )

    return fig
