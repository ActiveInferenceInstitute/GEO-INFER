"""
Visualization utilities for Bayesian geospatial models.

This module provides visualization functions for posterior
distributions, spatial predictions, and uncertainty quantification.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, List, Optional, Tuple, Union, Any


def plot_posterior(samples: Dict[str, np.ndarray], parameters: Optional[List[str]] = None) -> plt.Figure:
    """
    Plot posterior distributions for model parameters.

    Args:
        samples: Dictionary of parameter samples
        parameters: List of parameters to plot (if None, plot all)

    Returns:
        Matplotlib figure object
    """
    if parameters is None:
        parameters = list(samples.keys())

    n_params = len(parameters)
    fig, axes = plt.subplots(n_params, 2, figsize=(12, 4 * n_params))

    if n_params == 1:
        axes = axes.reshape(1, -1)

    for i, param in enumerate(parameters):
        param_samples = samples[param]
        if param_samples.ndim > 1:
            param_samples = param_samples.flatten()

        # Histogram
        axes[i, 0].hist(param_samples, bins=50, density=True, alpha=0.7)
        axes[i, 0].set_xlabel(param)
        axes[i, 0].set_ylabel('Density')
        axes[i, 0].set_title(f'Posterior Distribution: {param}')

        # Trace plot (simplified)
        axes[i, 1].plot(param_samples)
        axes[i, 1].set_xlabel('Sample Index')
        axes[i, 1].set_ylabel(param)
        axes[i, 1].set_title(f'Trace Plot: {param}')

    plt.tight_layout()
    return fig


def plot_spatial_prediction(
    spatial_coords: np.ndarray,
    predictions: np.ndarray,
    observations: Optional[np.ndarray] = None,
    uncertainty: Optional[np.ndarray] = None
) -> plt.Figure:
    """
    Plot spatial predictions with optional uncertainty.

    Args:
        spatial_coords: Spatial coordinates
        predictions: Predicted values
        observations: Observed values (optional)
        uncertainty: Prediction uncertainty (optional)

    Returns:
        Matplotlib figure object
    """
    fig, axes = plt.subplots(1, 2 if uncertainty is not None else 1, figsize=(15, 6))

    # Mean prediction
    sc = axes[0].scatter(spatial_coords[:, 0], spatial_coords[:, 1],
                        c=predictions, cmap='viridis', s=50)
    axes[0].set_xlabel('X coordinate')
    axes[0].set_ylabel('Y coordinate')
    axes[0].set_title('Mean Predictions')
    plt.colorbar(sc, ax=axes[0])

    # Observations
    if observations is not None:
        axes[0].scatter(spatial_coords[:, 0], spatial_coords[:, 1],
                       c='red', marker='x', s=30, label='Observations')
        axes[0].legend()

    # Uncertainty
    if uncertainty is not None:
        sc_unc = axes[1].scatter(spatial_coords[:, 0], spatial_coords[:, 1],
                                c=uncertainty, cmap='plasma', s=50)
        axes[1].set_xlabel('X coordinate')
        axes[1].set_ylabel('Y coordinate')
        axes[1].set_title('Prediction Uncertainty')
        plt.colorbar(sc_unc, ax=axes[1])

    plt.tight_layout()
    return fig


def plot_uncertainty(
    predictions: np.ndarray,
    uncertainty: np.ndarray,
    confidence_level: float = 0.95
) -> plt.Figure:
    """
    Plot prediction uncertainty with confidence intervals.

    Args:
        predictions: Predicted mean values
        uncertainty: Prediction standard deviations
        confidence_level: Confidence level for intervals

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Compute confidence intervals
    z_score = stats.norm.ppf((1 + confidence_level) / 2)
    lower_bound = predictions - z_score * uncertainty
    upper_bound = predictions + z_score * uncertainty

    # Plot mean predictions
    ax.plot(predictions, 'b-', linewidth=2, label='Predictions')

    # Plot confidence intervals
    ax.fill_between(range(len(predictions)), lower_bound, upper_bound,
                   alpha=0.3, color='blue', label=f'{confidence_level:.0%} Confidence Interval')

    ax.set_xlabel('Location Index')
    ax.set_ylabel('Value')
    ax.set_title('Predictions with Uncertainty')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_model_comparison(models: List[str], metrics: Dict[str, List[float]]) -> plt.Figure:
    """
    Plot comparison of different models.

    Args:
        models: List of model names
        metrics: Dictionary of metrics for each model

    Returns:
        Matplotlib figure object
    """
    fig, axes = plt.subplots(1, len(metrics), figsize=(6 * len(metrics), 5))

    if len(metrics) == 1:
        axes = [axes]

    for i, (metric_name, values) in enumerate(metrics.items()):
        axes[i].bar(models, values)
        axes[i].set_title(f'Model Comparison: {metric_name}')
        axes[i].set_ylabel(metric_name)
        axes[i].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    return fig
