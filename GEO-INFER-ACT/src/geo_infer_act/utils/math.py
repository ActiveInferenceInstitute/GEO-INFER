"""
Mathematical utilities for active inference models.
"""
from typing import Union, Optional
import numpy as np


def kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-10) -> float:
    """
    Compute KL divergence between distributions p and q.
    
    Args:
        p: First probability distribution
        q: Second probability distribution
        eps: Small constant to avoid numerical issues
        
    Returns:
        KL divergence value
    """
    # Ensure p and q are valid probability distributions
    p = np.asarray(p)
    q = np.asarray(q)
    
    # Normalize if not normalized
    if np.abs(np.sum(p) - 1.0) > eps:
        p = p / np.sum(p)
    
    if np.abs(np.sum(q) - 1.0) > eps:
        q = q / np.sum(q)
    
    # Add small constant to avoid log(0)
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    
    # Compute KL divergence
    return np.sum(p * np.log(p / q))


def entropy(p: np.ndarray, eps: float = 1e-10) -> float:
    """
    Compute entropy of a probability distribution.
    
    Args:
        p: Probability distribution
        eps: Small constant to avoid numerical issues
        
    Returns:
        Entropy value
    """
    # Ensure p is a valid probability distribution
    p = np.asarray(p)
    
    # Normalize if not normalized
    if np.abs(np.sum(p) - 1.0) > eps:
        p = p / np.sum(p)
    
    # Add small constant to avoid log(0)
    p = np.clip(p, eps, 1.0)
    
    # Compute entropy
    return -np.sum(p * np.log(p))


def precision_weighted_error(
    error: np.ndarray, 
    precision: Union[float, np.ndarray]
) -> float:
    """
    Compute precision-weighted prediction error.
    
    Args:
        error: Prediction error vector
        precision: Precision matrix or scalar
        
    Returns:
        Precision-weighted error
    """
    error = np.asarray(error)
    
    if isinstance(precision, (int, float)):
        return precision * np.sum(error ** 2)
    else:
        precision = np.asarray(precision)
        return error.T @ precision @ error


def softmax(x: np.ndarray, temp: float = 1.0) -> np.ndarray:
    """
    Compute softmax of vector x with temperature parameter.
    
    Args:
        x: Input vector
        temp: Temperature parameter
        
    Returns:
        Softmax probabilities
    """
    x = np.asarray(x)
    x_temp = x / temp
    exp_x = np.exp(x_temp - np.max(x_temp))  # Subtract max for numerical stability
    return exp_x / np.sum(exp_x)


def gaussian_log_likelihood(
    x: np.ndarray, 
    mean: np.ndarray, 
    precision: np.ndarray
) -> float:
    """
    Compute log likelihood under a Gaussian distribution.
    
    Args:
        x: Input vector
        mean: Mean vector
        precision: Precision matrix
        
    Returns:
        Log likelihood
    """
    x = np.asarray(x)
    mean = np.asarray(mean)
    precision = np.asarray(precision)
    
    dim = len(mean)
    error = x - mean
    
    # Compute log likelihood
    log_prob = -0.5 * (
        error.T @ precision @ error + 
        dim * np.log(2 * np.pi) - 
        np.log(np.linalg.det(precision))
    )
    
    return log_prob 