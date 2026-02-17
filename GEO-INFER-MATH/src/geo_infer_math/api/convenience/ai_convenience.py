"""
AI/ML Convenience Methods

This module provides convenience methods for AI and machine learning operations,
including gradient helpers, loss functions, and optimization wrappers.
"""

import numpy as np
from typing import Union, Optional, List, Tuple, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


def gradient_helper(
    function: Callable,
    parameters: np.ndarray,
    method: str = 'finite_difference',
    epsilon: float = 1e-6
) -> np.ndarray:
    """
    Helper for computing gradients.

    Args:
        function: Function to differentiate
        parameters: Parameter values
        method: Gradient method ('finite_difference', 'automatic')
        epsilon: Step size for finite differences

    Returns:
        Gradient vector
    """
    parameters = np.asarray(parameters).flatten()
    n_params = len(parameters)
    gradient = np.zeros(n_params)
    
    if method == 'finite_difference':
        # Finite difference approximation
        for i in range(n_params):
            params_plus = parameters.copy()
            params_plus[i] += epsilon
            params_minus = parameters.copy()
            params_minus[i] -= epsilon
            
            gradient[i] = (function(params_plus) - function(params_minus)) / (2 * epsilon)
    
    elif method == 'automatic':
        # Would use automatic differentiation if available
        # For now, fall back to finite differences
        return gradient_helper(function, parameters, method='finite_difference', epsilon=epsilon)
    
    return gradient


def spatial_loss_function(
    predictions: np.ndarray,
    targets: np.ndarray,
    coordinates: Optional[np.ndarray] = None,
    loss_type: str = 'mse',
    spatial_weight: float = 0.0
) -> float:
    """
    Spatial loss function for neural networks.

    Args:
        predictions: Predicted values
        targets: Target values
        coordinates: Optional spatial coordinates
        loss_type: Loss type ('mse', 'mae', 'huber')
        spatial_weight: Weight for spatial regularization

    Returns:
        Loss value
    """
    predictions = np.asarray(predictions).flatten()
    targets = np.asarray(targets).flatten()
    
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have same length")
    
    # Base loss
    if loss_type == 'mse':
        base_loss = np.mean((predictions - targets) ** 2)
    elif loss_type == 'mae':
        base_loss = np.mean(np.abs(predictions - targets))
    elif loss_type == 'huber':
        delta = 1.0
        error = predictions - targets
        base_loss = np.mean(np.where(
            np.abs(error) < delta,
            0.5 * error ** 2,
            delta * (np.abs(error) - 0.5 * delta)
        ))
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")
    
    # Spatial regularization
    spatial_loss = 0.0
    if coordinates is not None and spatial_weight > 0:
        coordinates = np.asarray(coordinates)
        if len(coordinates) == len(predictions):
            # Spatial smoothness regularization
            from scipy.spatial.distance import pdist, squareform
            distances = squareform(pdist(coordinates))
            pred_diff = np.abs(predictions[:, None] - predictions[None, :])
            spatial_loss = np.mean(pred_diff * np.exp(-distances))
    
    total_loss = base_loss + spatial_weight * spatial_loss
    
    return float(total_loss)


def optimization_wrapper(
    objective: Callable,
    initial_guess: np.ndarray,
    method: str = 'gradient_descent',
    **kwargs
) -> Tuple[np.ndarray, float, Dict[str, Any]]:
    """
    Wrapper for optimization algorithms.

    Args:
        objective: Objective function
        initial_guess: Initial parameter guess
        method: Optimization method
        **kwargs: Additional parameters

    Returns:
        Tuple of (optimal_parameters, optimal_value, metadata)
    """
    from geo_infer_math.core.optimization import Optimizer, GradientDescentOptimizer
    
    initial_guess = np.asarray(initial_guess)
    
    if method == 'gradient_descent':
        optimizer = GradientDescentOptimizer()
        result = optimizer.optimize(objective, initial_guess, **kwargs)
        return result.x, result.fun, {'method': method, 'iterations': result.nit}
    else:
        # Use generic optimizer
        optimizer = Optimizer()
        result = optimizer.optimize(objective, initial_guess, method=method, **kwargs)
        return result.x, result.fun, {'method': method}


class AIConvenience:
    """
    Convenience class for AI/ML operations.
    
    Provides high-level methods for common AI tasks.
    """
    
    def __init__(self):
        """Initialize AI convenience class."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._gradient_cache: Dict[str, np.ndarray] = {}
        self.logger.debug("AIConvenience initialized")
    
    def compute_gradient(
        self,
        function: Callable,
        parameters: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        """
        Compute gradient.
        
        Args:
            function: Function to differentiate
            parameters: Parameter values
            **kwargs: Additional parameters
        
        Returns:
            Gradient vector
        """
        return gradient_helper(function, parameters, **kwargs)
    
    def calculate_loss(
        self,
        predictions: np.ndarray,
        targets: np.ndarray,
        **kwargs
    ) -> float:
        """
        Calculate loss.
        
        Args:
            predictions: Predictions
            targets: Targets
            **kwargs: Additional parameters
        
        Returns:
            Loss value
        """
        return spatial_loss_function(predictions, targets, **kwargs)
    
    def optimize(
        self,
        objective: Callable,
        initial_guess: np.ndarray,
        **kwargs
    ) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        """
        Optimize objective function.
        
        Args:
            objective: Objective function
            initial_guess: Initial guess
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (optimal_parameters, optimal_value, metadata)
        """
        return optimization_wrapper(objective, initial_guess, **kwargs)

