"""
Validation Utilities Module

This module provides functions for validating inputs and data structures
used throughout the GEO-INFER-MATH library.
"""

import numpy as np
from typing import Union, List, Tuple, Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)

def validate_coordinates(coordinates: np.ndarray,
                        min_dims: int = 2,
                        max_dims: int = 3,
                        allow_none: bool = False) -> bool:
    """
    Validate coordinate array.

    Args:
        coordinates: Array of coordinates
        min_dims: Minimum number of dimensions
        max_dims: Maximum number of dimensions
        allow_none: Whether to allow None values

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If coordinates are invalid
    """
    if coordinates is None:
        if allow_none:
            return True
        else:
            raise ValueError("Coordinates cannot be None")

    if not isinstance(coordinates, np.ndarray):
        raise ValueError(f"Coordinates must be a numpy array, got {type(coordinates)}")

    if coordinates.ndim != 2:
        raise ValueError(f"Coordinates must be a 2D array, got {coordinates.ndim}D")

    n_samples, n_dims = coordinates.shape

    if n_samples == 0:
        raise ValueError("Coordinates array is empty")

    if n_dims < min_dims:
        raise ValueError(f"Coordinates must have at least {min_dims} dimensions, got {n_dims}")

    if n_dims > max_dims:
        raise ValueError(f"Coordinates cannot have more than {max_dims} dimensions, got {n_dims}")

    # Check for NaN and infinite values
    if np.any(np.isnan(coordinates)):
        raise ValueError("Coordinates contain NaN values")

    if np.any(np.isinf(coordinates)):
        raise ValueError("Coordinates contain infinite values")

    # Check for reasonable coordinate ranges (for geographic coordinates)
    if n_dims >= 2:
        lon_range = np.ptp(coordinates[:, 0])
        lat_range = np.ptp(coordinates[:, 1])

        # Warn if ranges seem unreasonable for geographic coordinates
        if lon_range > 360:
            logger.warning(f"Longitude range ({lon_range}) seems unusually large")
        if lat_range > 180:
            logger.warning(f"Latitude range ({lat_range}) seems unusually large")

    return True

def validate_matrix(matrix: np.ndarray,
                   square: bool = False,
                   symmetric: bool = False,
                   positive_definite: bool = False,
                   allow_none: bool = False) -> bool:
    """
    Validate matrix properties.

    Args:
        matrix: Input matrix
        square: Whether matrix must be square
        symmetric: Whether matrix must be symmetric
        positive_definite: Whether matrix must be positive definite
        allow_none: Whether to allow None values

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If matrix is invalid
    """
    if matrix is None:
        if allow_none:
            return True
        else:
            raise ValueError("Matrix cannot be None")

    if not isinstance(matrix, np.ndarray):
        raise ValueError(f"Matrix must be a numpy array, got {type(matrix)}")

    if matrix.ndim != 2:
        raise ValueError(f"Matrix must be a 2D array, got {matrix.ndim}D")

    n_rows, n_cols = matrix.shape

    if square and n_rows != n_cols:
        raise ValueError(f"Square matrix required, got shape {matrix.shape}")

    # Check for NaN and infinite values
    if np.any(np.isnan(matrix)):
        raise ValueError("Matrix contains NaN values")

    if np.any(np.isinf(matrix)):
        raise ValueError("Matrix contains infinite values")

    if symmetric and not np.allclose(matrix, matrix.T, atol=1e-10):
        raise ValueError("Matrix is not symmetric")

    if positive_definite:
        if not square:
            raise ValueError("Positive definite check requires square matrix")

        try:
            eigenvalues = np.linalg.eigvals(matrix)
            if np.any(eigenvalues <= 0):
                raise ValueError("Matrix is not positive definite")
        except np.linalg.LinAlgError:
            raise ValueError("Cannot determine if matrix is positive definite")

    return True

def validate_weights_matrix(weights_matrix: np.ndarray,
                          n_points: Optional[int] = None) -> bool:
    """
    Validate spatial weights matrix.

    Args:
        weights_matrix: Spatial weights matrix
        n_points: Expected number of points (if known)

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If weights matrix is invalid
    """
    validate_matrix(weights_matrix, square=True)

    n = weights_matrix.shape[0]

    if n_points is not None and n != n_points:
        raise ValueError(f"Weights matrix size ({n}) does not match expected size ({n_points})")

    # Check diagonal is zero (no self-weights)
    diagonal = np.diag(weights_matrix)
    if not np.allclose(diagonal, 0, atol=1e-10):
        logger.warning("Weights matrix diagonal is not zero - self-weights detected")

    # Check non-negative weights
    if np.any(weights_matrix < 0):
        logger.warning("Weights matrix contains negative values")

    # Check row sums (should typically be 1 for row-standardized matrices)
    row_sums = weights_matrix.sum(axis=1)
    if not np.allclose(row_sums, 1.0, atol=0.1):
        logger.info("Weights matrix does not appear to be row-standardized")

    return True

def validate_values_array(values: np.ndarray,
                         n_points: Optional[int] = None,
                         allow_none: bool = False) -> bool:
    """
    Validate values array.

    Args:
        values: Array of values
        n_points: Expected number of points (if known)
        allow_none: Whether to allow None values

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If values array is invalid
    """
    if values is None:
        if allow_none:
            return True
        else:
            raise ValueError("Values cannot be None")

    if not isinstance(values, np.ndarray):
        raise ValueError(f"Values must be a numpy array, got {type(values)}")

    if values.ndim != 1:
        raise ValueError(f"Values must be a 1D array, got {values.ndim}D")

    n_values = len(values)

    if n_values == 0:
        raise ValueError("Values array is empty")

    if n_points is not None and n_values != n_points:
        raise ValueError(f"Values array size ({n_values}) does not match expected size ({n_points})")

    # Check for NaN and infinite values
    if np.any(np.isnan(values)):
        raise ValueError("Values contain NaN values")

    if np.any(np.isinf(values)):
        raise ValueError("Values contain infinite values")

    return True

def validate_bounds(bounds: List[Tuple[float, float]],
                   n_params: Optional[int] = None) -> bool:
    """
    Validate parameter bounds for optimization.

    Args:
        bounds: List of (min, max) tuples
        n_params: Expected number of parameters

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If bounds are invalid
    """
    if not isinstance(bounds, list):
        raise ValueError(f"Bounds must be a list, got {type(bounds)}")

    if n_params is not None and len(bounds) != n_params:
        raise ValueError(f"Bounds length ({len(bounds)}) does not match expected parameters ({n_params})")

    for i, bound in enumerate(bounds):
        if not isinstance(bound, tuple) or len(bound) != 2:
            raise ValueError(f"Bound {i} must be a tuple of (min, max), got {bound}")

        min_val, max_val = bound

        if not isinstance(min_val, (int, float)):
            raise ValueError(f"Bound {i} min value must be numeric, got {type(min_val)}")

        if not isinstance(max_val, (int, float)):
            raise ValueError(f"Bound {i} max value must be numeric, got {type(max_val)}")

        if min_val >= max_val:
            raise ValueError(f"Bound {i} min ({min_val}) must be less than max ({max_val})")

    return True

def validate_function_input(func: Callable,
                          n_args: Optional[int] = None,
                          domain: Optional[List[Tuple[float, float]]] = None) -> bool:
    """
    Validate function input properties.

    Args:
        func: Function to validate
        n_args: Expected number of arguments
        domain: Valid domain for function arguments

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If function is invalid
    """
    if not callable(func):
        raise ValueError(f"Input must be callable, got {type(func)}")

    # Test function with sample input
    if n_args is not None:
        try:
            sample_args = [1.0] * n_args
            result = func(*sample_args)

            if not isinstance(result, (int, float, np.ndarray)):
                logger.warning(f"Function returns unexpected type: {type(result)}")

        except Exception as e:
            raise ValueError(f"Function cannot be evaluated with {n_args} arguments: {e}")

    if domain is not None:
        try:
            for bound in domain:
                test_point = [(bound[0] + bound[1]) / 2]  # Midpoint of bounds
                result = func(*test_point)
        except Exception as e:
            raise ValueError(f"Function domain validation failed: {e}")

    return True

def validate_spatial_autocorrelation_params(values: np.ndarray,
                                          coordinates: np.ndarray,
                                          weights_matrix: Optional[np.ndarray] = None) -> bool:
    """
    Validate parameters for spatial autocorrelation analysis.

    Args:
        values: Array of values
        coordinates: Array of coordinates
        weights_matrix: Optional spatial weights matrix

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If parameters are invalid
    """
    validate_values_array(values)
    validate_coordinates(coordinates)

    if len(values) != len(coordinates):
        raise ValueError(f"Values ({len(values)}) and coordinates ({len(coordinates)}) must have same length")

    if weights_matrix is not None:
        validate_weights_matrix(weights_matrix, n_points=len(values))

    return True

def validate_interpolation_params(known_points: np.ndarray,
                                known_values: np.ndarray,
                                query_points: np.ndarray) -> bool:
    """
    Validate parameters for spatial interpolation.

    Args:
        known_points: Known point coordinates
        known_values: Known point values
        query_points: Query point coordinates

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If parameters are invalid
    """
    validate_coordinates(known_points)
    validate_values_array(known_values)
    validate_coordinates(query_points)

    if len(known_values) != len(known_points):
        raise ValueError(f"Known values ({len(known_values)}) and points ({len(known_points)}) must have same length")

    # Check for sufficient data points
    if len(known_points) < 3:
        logger.warning("Very few known points for interpolation - results may be unreliable")

    return True

def validate_clustering_params(X: np.ndarray,
                             coordinates: Optional[np.ndarray] = None,
                             n_clusters: Optional[int] = None) -> bool:
    """
    Validate parameters for clustering analysis.

    Args:
        X: Feature matrix
        coordinates: Optional spatial coordinates
        n_clusters: Number of clusters

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If parameters are invalid
    """
    if not isinstance(X, np.ndarray):
        raise ValueError(f"Feature matrix must be a numpy array, got {type(X)}")

    if X.ndim != 2:
        raise ValueError(f"Feature matrix must be 2D, got {X.ndim}D")

    n_samples, n_features = X.shape

    if n_samples == 0:
        raise ValueError("Feature matrix is empty")

    if coordinates is not None:
        validate_coordinates(coordinates)
        if len(coordinates) != n_samples:
            raise ValueError(f"Coordinates ({len(coordinates)}) and features ({n_samples}) must have same number of samples")

    if n_clusters is not None:
        if not isinstance(n_clusters, int) or n_clusters <= 0:
            raise ValueError(f"Number of clusters must be a positive integer, got {n_clusters}")

        if n_clusters > n_samples:
            raise ValueError(f"Number of clusters ({n_clusters}) cannot exceed number of samples ({n_samples})")

    return True

def validate_tensor_data(tensor: np.ndarray,
                        expected_dims: Optional[int] = None) -> bool:
    """
    Validate tensor data structure.

    Args:
        tensor: Input tensor
        expected_dims: Expected number of dimensions

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If tensor is invalid
    """
    if not isinstance(tensor, np.ndarray):
        raise ValueError(f"Tensor must be a numpy array, got {type(tensor)}")

    if expected_dims is not None and tensor.ndim != expected_dims:
        raise ValueError(f"Tensor must have {expected_dims} dimensions, got {tensor.ndim}")

    if tensor.size == 0:
        raise ValueError("Tensor is empty")

    # Check for NaN and infinite values
    if np.any(np.isnan(tensor)):
        raise ValueError("Tensor contains NaN values")

    if np.any(np.isinf(tensor)):
        raise ValueError("Tensor contains infinite values")

    return True

__all__ = [
    "validate_coordinates",
    "validate_matrix",
    "validate_weights_matrix",
    "validate_values_array",
    "validate_bounds",
    "validate_function_input",
    "validate_spatial_autocorrelation_params",
    "validate_interpolation_params",
    "validate_clustering_params",
    "validate_tensor_data"
]
