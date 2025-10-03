"""
Diagnostics for Bayesian inference.

This module provides diagnostic tools for assessing
convergence and quality of Bayesian inference.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any


def mcmc_diagnostics(samples: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """
    Compute MCMC diagnostics for posterior samples.

    Args:
        samples: Dictionary of parameter samples

    Returns:
        Dictionary of diagnostic metrics
    """
    diagnostics = {}

    for param, param_samples in samples.items():
        # Reshape if needed
        if param_samples.ndim > 1:
            param_samples = param_samples.flatten()

        # Basic statistics
        diagnostics[param] = {
            'mean': np.mean(param_samples),
            'std': np.std(param_samples),
            'median': np.median(param_samples),
            'q25': np.percentile(param_samples, 25),
            'q75': np.percentile(param_samples, 75),
            'min': np.min(param_samples),
            'max': np.max(param_samples),
        }

        # Effective sample size (simplified)
        n_samples = len(param_samples)
        autocorr = np.corrcoef(param_samples[:-1], param_samples[1:])[0, 1]
        if autocorr > 0:
            diagnostics[param]['ess'] = n_samples / (1 + 2 * np.sum([autocorr**k for k in range(1, min(100, n_samples//2))]))
        else:
            diagnostics[param]['ess'] = n_samples

        # R-hat (simplified for single chain)
        diagnostics[param]['r_hat'] = 1.0  # Would need multiple chains for proper R-hat

    return diagnostics


def convergence_metrics(samples: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """
    Compute convergence metrics for MCMC samples.

    Args:
        samples: Dictionary of parameter samples

    Returns:
        Dictionary of convergence metrics
    """
    metrics = {}

    for param, param_samples in samples.items():
        # Reshape if needed
        if param_samples.ndim > 1:
            param_samples = param_samples.flatten()

        # Gelman-Rubin statistic (simplified)
        # In practice, this would compare multiple chains
        metrics[param] = {
            'potential_scale_reduction': 1.0,  # Placeholder
            'monte_carlo_se': np.std(param_samples) / np.sqrt(len(param_samples)),
        }

        # Geweke diagnostic (simplified)
        n = len(param_samples)
        n1 = n // 2
        n2 = n - n1

        mean1 = np.mean(param_samples[:n1])
        mean2 = np.mean(param_samples[n1:])

        var1 = np.var(param_samples[:n1])
        var2 = np.var(param_samples[n1:])

        if var1 > 0 and var2 > 0:
            geweke_z = (mean1 - mean2) / np.sqrt(var1/n1 + var2/n2)
            metrics[param]['geweke_z'] = geweke_z
        else:
            metrics[param]['geweke_z'] = 0.0

    return metrics
