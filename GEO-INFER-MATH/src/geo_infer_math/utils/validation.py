"""
Validation Utilities

This module provides validation decorators and utilities for
mathematical operations.
"""

import functools
import numpy as np
from typing import Callable, Optional, Tuple, Any
import logging

from geo_infer_math.utils.exceptions import (
    InvalidDistributionError,
    NumericalError,
    SpatialError,
)

logger = logging.getLogger(__name__)


def validate_probabilities(func: Callable) -> Callable:
    """Decorator to validate probability distributions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check for probability arguments
        for arg in args:
            if isinstance(arg, np.ndarray):
                if np.any(arg < 0):
                    raise InvalidDistributionError("Probabilities must be non-negative")
                if not np.isclose(np.sum(arg), 1.0, rtol=1e-10):
                    if np.sum(arg) > 0:
                        logger.warning("Probabilities don't sum to 1, normalizing")
                    else:
                        raise InvalidDistributionError("Probabilities must sum to positive value")
        
        return func(*args, **kwargs)
    
    return wrapper


def validate_coordinates(func: Callable) -> Callable:
    """Decorator to validate spatial coordinates."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check for coordinate arguments
        for arg in args:
            if isinstance(arg, np.ndarray) and arg.ndim == 2:
                if arg.shape[1] not in [2, 3]:
                    raise SpatialError(f"Coordinates must be 2D or 3D, got shape {arg.shape}")
                if np.any(np.isnan(arg)) or np.any(np.isinf(arg)):
                    raise SpatialError("Coordinates contain NaN or Inf values")
        
        return func(*args, **kwargs)
    
    return wrapper


def validate_numerical(func: Callable) -> Callable:
    """Decorator to validate numerical inputs."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check for numerical arguments
        for arg in args:
            if isinstance(arg, (int, float, np.number)):
                if np.isnan(arg) or np.isinf(arg):
                    raise NumericalError(f"Invalid numerical value: {arg}")
        
        return func(*args, **kwargs)
    
    return wrapper


def validate_shape(expected_shape: Tuple[int, ...], axis: int = 0):
    """
    Decorator to validate array shapes.
    
    Args:
        expected_shape: Expected shape tuple
        axis: Which argument to check (0 = first, 1 = second, etc.)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) > axis:
                arg = args[axis]
                if isinstance(arg, np.ndarray):
                    if arg.shape != expected_shape:
                        raise ValueError(
                            f"Expected shape {expected_shape}, got {arg.shape}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def validate_range(param_name: str, min_val: float, max_val: float):
    """
    Decorator to validate parameter ranges.
    
    Args:
        param_name: Name of parameter to validate
        min_val: Minimum value
        max_val: Maximum value
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check in kwargs first
            if param_name in kwargs:
                val = kwargs[param_name]
                if not (min_val <= val <= max_val):
                    raise ValueError(
                        f"{param_name} must be between {min_val} and {max_val}, got {val}"
                    )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
