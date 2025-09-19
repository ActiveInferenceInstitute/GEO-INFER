"""
Data validation utilities for GEO-INFER-SPM

This module provides functions for validating SPM data structures,
design matrices, and analysis parameters to ensure data quality
and compatibility with SPM statistical methods.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import warnings

from ..models.data_models import SPMData, DesignMatrix


def validate_spm_data(data: SPMData) -> SPMData:
    """
    Validate SPMData object for consistency and data quality.

    Args:
        data: SPMData object to validate

    Returns:
        Validated SPMData (may be modified if issues are fixed)

    Raises:
        ValueError: If validation fails and cannot be automatically fixed
    """
    issues = []

    # Validate data array
    if not hasattr(data, 'data') or data.data is None:
        raise ValueError("SPMData must contain data array")

    # Convert data to numpy array if needed
    if not isinstance(data.data, np.ndarray):
        try:
            data.data = np.asarray(data.data)
        except Exception as e:
            raise ValueError(f"Cannot convert data to numpy array: {e}")

    # Check data dimensionality
    if data.data.ndim > 2:
        warnings.warn(f"Data has {data.data.ndim} dimensions. SPM typically works with 1D or 2D data.")

    # Validate coordinates
    if not hasattr(data, 'coordinates') or data.coordinates is None:
        raise ValueError("SPMData must contain coordinate information")

    data.coordinates = np.asarray(data.coordinates)

    if data.coordinates.shape[1] != 2:
        raise ValueError(f"Coordinates must have shape (n_points, 2), got {data.coordinates.shape}")

    # Check coordinate-data consistency
    expected_n_points = data.coordinates.shape[0]
    actual_n_points = data.data.shape[0] if data.data.ndim > 1 else len(data.data)

    if expected_n_points != actual_n_points:
        raise ValueError(f"Coordinate count ({expected_n_points}) does not match data count ({actual_n_points})")

    # Validate temporal data if present
    if data.time is not None:
        data.time = np.asarray(data.time)
        if len(data.time) != expected_n_points:
            raise ValueError(f"Time array length ({len(data.time)}) does not match data count ({expected_n_points})")

    # Validate covariates if present
    if data.covariates is not None:
        for name, values in data.covariates.items():
            values_array = np.asarray(values)
            if len(values_array) != expected_n_points:
                raise ValueError(f"Covariate '{name}' length ({len(values_array)}) does not match data count ({expected_n_points})")
            data.covariates[name] = values_array

    # Check for NaN/inf values
    if np.any(np.isnan(data.data)):
        nan_count = np.sum(np.isnan(data.data))
        warnings.warn(f"Data contains {nan_count} NaN values")

    if np.any(np.isinf(data.data)):
        inf_count = np.sum(np.isinf(data.data))
        warnings.warn(f"Data contains {inf_count} infinite values")

    # Validate coordinate ranges for common CRS
    if hasattr(data, 'crs') and data.crs:
        crs_str = str(data.crs).upper()
        if '4326' in crs_str or 'WGS84' in crs_str:
            lon, lat = data.coordinates[:, 0], data.coordinates[:, 1]
            if np.any((lon < -180) | (lon > 180)):
                warnings.warn("Longitude values outside valid range [-180, 180]")
            if np.any((lat < -90) | (lat > 90)):
                warnings.warn("Latitude values outside valid range [-90, 90]")

    # Update metadata with validation results
    if not hasattr(data, 'metadata'):
        data.metadata = {}

    data.metadata['validation'] = {
        'passed': True,
        'n_points': expected_n_points,
        'data_shape': data.data.shape,
        'data_dtype': str(data.data.dtype),
        'has_temporal': data.time is not None,
        'has_covariates': data.covariates is not None,
        'crs': getattr(data, 'crs', None)
    }

    return data


def validate_design_matrix(design_matrix: DesignMatrix,
                          n_points: Optional[int] = None) -> DesignMatrix:
    """
    Validate design matrix for GLM analysis.

    Args:
        design_matrix: DesignMatrix object to validate
        n_points: Expected number of data points

    Returns:
        Validated DesignMatrix

    Raises:
        ValueError: If validation fails
    """
    # Validate matrix structure
    if not hasattr(design_matrix, 'matrix') or design_matrix.matrix is None:
        raise ValueError("DesignMatrix must contain matrix array")

    design_matrix.matrix = np.asarray(design_matrix.matrix)

    if design_matrix.matrix.ndim != 2:
        raise ValueError(f"Design matrix must be 2D, got {design_matrix.matrix.ndim}D")

    n_points_matrix, n_regressors = design_matrix.matrix.shape

    if n_points is not None and n_points_matrix != n_points:
        raise ValueError(f"Design matrix rows ({n_points_matrix}) does not match data points ({n_points})")

    # Validate names
    if hasattr(design_matrix, 'names') and design_matrix.names:
        if len(design_matrix.names) != n_regressors:
            raise ValueError(f"Number of names ({len(design_matrix.names)}) does not match number of regressors ({n_regressors})")
    else:
        # Generate default names
        design_matrix.names = [f'regressor_{i}' for i in range(n_regressors)]

    # Check for rank deficiency
    rank = np.linalg.matrix_rank(design_matrix.matrix)
    if rank < n_regressors:
        warnings.warn(f"Design matrix is rank deficient: rank {rank} < {n_regressors} regressors")

    # Check for multicollinearity
    if n_regressors > 1:
        corr_matrix = np.corrcoef(design_matrix.matrix.T)
        np.fill_diagonal(corr_matrix, 0)  # Ignore self-correlations
        max_corr = np.max(np.abs(corr_matrix))

        if max_corr > 0.9:
            warnings.warn(f"High multicollinearity detected (max correlation: {max_corr:.3f})")

    # Validate factors if present
    if hasattr(design_matrix, 'factors') and design_matrix.factors:
        _validate_factors(design_matrix)

    # Check condition number
    condition_number = np.linalg.cond(design_matrix.matrix)
    if condition_number > 1e10:
        warnings.warn(f"Design matrix is ill-conditioned (condition number: {condition_number:.2e})")

    return design_matrix


def _validate_factors(design_matrix: DesignMatrix):
    """Validate categorical factors in design matrix."""
    if not hasattr(design_matrix, 'factors') or not design_matrix.factors:
        return

    for factor_name, levels in design_matrix.factors.items():
        if not isinstance(levels, list):
            raise ValueError(f"Factor '{factor_name}' levels must be a list")

        # Check if factor columns exist in design matrix
        factor_cols = [i for i, name in enumerate(design_matrix.names)
                      if name.startswith(f"{factor_name}_")]

        if len(factor_cols) == 0:
            warnings.warn(f"No columns found for factor '{factor_name}'")

        # Check if number of columns matches expected (n_levels - 1 for dummy coding)
        expected_cols = len(levels) - 1
        if len(factor_cols) != expected_cols:
            warnings.warn(f"Factor '{factor_name}' has {len(factor_cols)} columns, expected {expected_cols}")


def validate_contrast(contrast_vector: np.ndarray, n_regressors: int,
                     contrast_type: str = 't') -> np.ndarray:
    """
    Validate contrast vector for statistical testing.

    Args:
        contrast_vector: Contrast vector to validate
        n_regressors: Number of regressors in design matrix
        contrast_type: Type of contrast ('t' or 'F')

    Returns:
        Validated contrast vector

    Raises:
        ValueError: If contrast is invalid
    """
    contrast_vector = np.asarray(contrast_vector)

    if contrast_type.lower() == 't':
        if contrast_vector.ndim != 1:
            raise ValueError("T-contrast must be 1D vector")

        if len(contrast_vector) != n_regressors:
            raise ValueError(f"T-contrast length ({len(contrast_vector)}) does not match number of regressors ({n_regressors})")

    elif contrast_type.lower() == 'f':
        if contrast_vector.ndim != 2:
            raise ValueError("F-contrast must be 2D matrix")

        if contrast_vector.shape[1] != n_regressors:
            raise ValueError(f"F-contrast columns ({contrast_vector.shape[1]}) does not match number of regressors ({n_regressors})")

        if contrast_vector.shape[0] < 1:
            raise ValueError("F-contrast must have at least 1 row")

    else:
        raise ValueError(f"Unknown contrast type: {contrast_type}")

    # Check if contrast is not all zeros
    if np.allclose(contrast_vector, 0):
        warnings.warn("Contrast vector is all zeros - will result in zero statistic")

    return contrast_vector


def validate_spatial_autocorrelation(data: SPMData, max_lag: int = 10,
                                   alpha: float = 0.05) -> Dict[str, Any]:
    """
    Validate and assess spatial autocorrelation in data.

    Args:
        data: SPMData to analyze
        max_lag: Maximum lag distance for autocorrelation
        alpha: Significance level for tests

    Returns:
        Dictionary with autocorrelation analysis results
    """
    from scipy.spatial.distance import pdist, squareform

    # Compute distance matrix
    distances = squareform(pdist(data.coordinates))

    # Compute Moran's I statistic
    moran_results = _compute_morans_i(data.data, distances)

    # Compute Geary's C statistic
    geary_results = _compute_gearys_c(data.data, distances)

    # Variogram analysis
    variogram_results = _compute_variogram(data.data, distances, max_lag)

    results = {
        'morans_i': moran_results,
        'gearys_c': geary_results,
        'variogram': variogram_results,
        'spatial_dependence': _assess_spatial_dependence(moran_results, geary_results, alpha)
    }

    return results


def _compute_morans_i(data: np.ndarray, distance_matrix: np.ndarray) -> Dict[str, Any]:
    """Compute Moran's I statistic for spatial autocorrelation."""
    n = len(data)

    # Standardize data
    z = (data - np.mean(data)) / np.std(data)

    # Weight matrix (inverse distance)
    weights = 1 / (distance_matrix + np.eye(n) * 1e-10)  # Avoid self-weighting
    np.fill_diagonal(weights, 0)

    # Moran's I
    numerator = np.sum(weights * np.outer(z, z))
    denominator = np.sum(weights)
    morans_i = numerator / denominator

    # Expected value and variance under null
    expected_i = -1 / (n - 1)

    # Simplified variance calculation
    s1 = 0.5 * np.sum((weights + weights.T)**2)
    s2 = np.sum((np.sum(weights, axis=1) + np.sum(weights, axis=0))**2)
    s3 = (np.sum(weights)**2) / ((n - 1) * (n - 2))
    s4 = (n**2 - 3*n + 3) * s1 - n * s2 + 3 * s3
    s5 = (n**2 - n) * s1 - 2*n * s2 + 6 * s3

    var_i = s4 / ((n - 1) * (n - 2) * (n - 3) * np.sum(weights)**2) - s5 / ((n - 1) * (n - 2) * (n - 3))

    # Z-score
    z_score = (morans_i - expected_i) / np.sqrt(var_i)

    return {
        'statistic': morans_i,
        'expected': expected_i,
        'variance': var_i,
        'z_score': z_score,
        'p_value': 2 * (1 - stats.norm.cdf(abs(z_score)))
    }


def _compute_gearys_c(data: np.ndarray, distance_matrix: np.ndarray) -> Dict[str, Any]:
    """Compute Geary's C statistic for spatial autocorrelation."""
    n = len(data)
    weights = 1 / (distance_matrix + np.eye(n) * 1e-10)
    np.fill_diagonal(weights, 0)

    # Geary's C
    numerator = (n - 1) * np.sum(weights * (data[:, np.newaxis] - data[np.newaxis, :])**2)
    denominator = 2 * np.sum(weights) * np.sum((data - np.mean(data))**2)
    gearys_c = numerator / denominator

    # Expected value
    expected_c = 1

    return {
        'statistic': gearys_c,
        'expected': expected_c,
        'p_value': 2 * (1 - stats.norm.cdf(abs(gearys_c - expected_c) / 0.1))  # Approximate
    }


def _compute_variogram(data: np.ndarray, distance_matrix: np.ndarray,
                      max_lag: int) -> Dict[str, Any]:
    """Compute empirical variogram."""
    distances = distance_matrix.flatten()
    diffs = (data[:, np.newaxis] - data[np.newaxis, :])**2
    diff_values = diffs.flatten()

    # Remove self-comparisons
    mask = distances > 0
    distances = distances[mask]
    diff_values = diff_values[mask]

    # Bin distances
    bins = np.linspace(0, np.max(distances), max_lag + 1)
    variogram = []

    for i in range(max_lag):
        mask = (distances >= bins[i]) & (distances < bins[i+1])
        if np.sum(mask) > 0:
            gamma = np.mean(diff_values[mask]) / 2
            variogram.append(gamma)

    return {
        'lags': bins[:-1] + (bins[1] - bins[0]) / 2,
        'variogram': variogram,
        'n_pairs': [np.sum((distances >= bins[i]) & (distances < bins[i+1])) for i in range(max_lag)]
    }


def _assess_spatial_dependence(moran_results: Dict, geary_results: Dict,
                              alpha: float) -> str:
    """Assess overall spatial dependence."""
    moran_sig = moran_results['p_value'] < alpha
    geary_sig = geary_results['p_value'] < alpha

    if moran_sig and geary_sig:
        return "strong_spatial_dependence"
    elif moran_sig or geary_sig:
        return "moderate_spatial_dependence"
    else:
        return "no_spatial_dependence"
