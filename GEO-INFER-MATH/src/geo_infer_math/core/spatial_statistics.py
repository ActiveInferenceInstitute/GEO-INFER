"""
Spatial Statistics Module

This module provides functions and classes for analyzing spatial patterns,
autocorrelation, and distributions in geospatial data.
"""

import numpy as np
from typing import Union, List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass

@dataclass
class SpatialDescriptiveStats:
    """Container for spatial descriptive statistics."""
    mean: float
    median: float
    stdev: float
    variance: float
    min_value: float
    max_value: float
    centroid: Tuple[float, float]
    dispersion: float
    skewness: float
    kurtosis: float

class MoranI:
    """
    Implementation of Moran's I statistic for spatial autocorrelation.
    
    Moran's I measures the spatial autocorrelation (clustering or similarity)
    of values across geographic locations.
    """
    
    def __init__(self, weights_matrix: np.ndarray = None):
        """
        Initialize MoranI calculator.
        
        Args:
            weights_matrix: Spatial weights matrix defining relationships between locations
        """
        self.weights_matrix = weights_matrix
    
    def compute(self, values: np.ndarray, coords: np.ndarray = None) -> Dict[str, float]:
        """
        Compute Moran's I statistic.
        
        Args:
            values: Array of values at each location
            coords: Optional array of coordinates if weights_matrix is not provided
            
        Returns:
            Dictionary containing Moran's I statistic and p-value
        """
        if self.weights_matrix is None and coords is not None:
            # Generate weights matrix from coordinates (inverse distance)
            self.weights_matrix = self._generate_weights(coords)
        
        # Standardize values
        z = (values - np.mean(values)) / np.std(values)
        
        # Calculate Moran's I
        n = len(values)
        w_sum = np.sum(self.weights_matrix)
        
        # Numerator: spatial covariance
        numerator = np.sum(np.outer(z, z) * self.weights_matrix)
        
        # Denominator: variance
        denominator = np.sum(z**2)
        
        # Moran's I formula
        I = (n / w_sum) * (numerator / denominator)
        
        # Calculate expected I and variance for p-value computation
        expected_I = -1.0 / (n - 1)
        
        # Calculate variance (simplified formula)
        s1 = 0.5 * np.sum((self.weights_matrix + self.weights_matrix.T)**2)
        s2 = np.sum((np.sum(self.weights_matrix, axis=0) + np.sum(self.weights_matrix, axis=1))**2)
        var_I = (n**2 * s1 - n * s2 + 3 * w_sum**2) / ((n**2 - 1) * w_sum**2)
        
        # Calculate z-score and p-value
        z_score = (I - expected_I) / np.sqrt(var_I)
        
        # Two-tailed p-value (simplified calculation)
        p_value = 2 * (1 - np.abs(np.clip(z_score, -8, 8) / 8))
        
        return {
            "I": I,
            "expected_I": expected_I,
            "var_I": var_I,
            "z_score": z_score,
            "p_value": p_value
        }
    
    def _generate_weights(self, coords: np.ndarray) -> np.ndarray:
        """
        Generate a spatial weights matrix from coordinates.
        
        Args:
            coords: Array of coordinates (n x 2)
            
        Returns:
            Spatial weights matrix (n x n)
        """
        n = coords.shape[0]
        weights = np.zeros((n, n))
        
        # Calculate inverse distance weights
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Euclidean distance
                    dist = np.sqrt(np.sum((coords[i] - coords[j])**2))
                    weights[i, j] = 1.0 / max(dist, 1e-10)  # Avoid division by zero
        
        # Row standardize
        row_sums = weights.sum(axis=1)
        weights = weights / row_sums[:, np.newaxis]
        
        return weights

def getis_ord_g(values: np.ndarray, weights_matrix: np.ndarray) -> Dict[str, float]:
    """
    Calculate Getis-Ord G* statistic for hot spot analysis.
    
    Args:
        values: Array of values at each location
        weights_matrix: Spatial weights matrix
        
    Returns:
        Dictionary with G* statistics for each location and global G
    """
    n = len(values)
    sum_x = np.sum(values)
    mean_x = np.mean(values)
    sum_x_sq = np.sum(values**2)
    s = np.sqrt((sum_x_sq / n) - (mean_x**2))
    
    # Calculate G* for each location
    g_star = np.zeros(n)
    z_scores = np.zeros(n)
    
    for i in range(n):
        w_i = weights_matrix[i]
        sum_w = np.sum(w_i)
        sum_wx = np.sum(w_i * values)
        
        # Calculate G* statistic
        numerator = sum_wx - mean_x * sum_w
        
        # Calculate standard deviation
        ss = s * np.sqrt((n * sum_w**2 - sum_w**2) / (n - 1))
        
        # Store G* and calculate z-score
        if ss > 0:
            g_star[i] = sum_wx / sum_x
            z_scores[i] = numerator / ss
    
    # Calculate global G
    total_weights = np.sum(weights_matrix)
    global_g = np.sum(weights_matrix * np.outer(values, values)) / (total_weights * sum_x)
    
    return {
        "local_g": g_star,
        "z_scores": z_scores,
        "global_g": global_g
    }

def ripley_k(points: np.ndarray, distances: List[float], 
             area: float, boundary_correction: bool = True) -> Dict[str, np.ndarray]:
    """
    Calculate Ripley's K function for point pattern analysis.
    
    Args:
        points: Array of point coordinates (n x 2)
        distances: List of distances at which to calculate K
        area: Total area of the study region
        boundary_correction: Whether to apply edge correction
        
    Returns:
        Dictionary with K function values and L function transform
    """
    n_points = points.shape[0]
    k_values = np.zeros(len(distances))
    l_values = np.zeros(len(distances))
    
    # Calculate all pairwise distances
    dist_matrix = np.zeros((n_points, n_points))
    for i in range(n_points):
        for j in range(i+1, n_points):
            dist = np.sqrt(np.sum((points[i] - points[j])**2))
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    
    # Calculate K function for each distance
    for i, r in enumerate(distances):
        # Count points within distance r of each point
        count = np.sum(dist_matrix <= r) - n_points  # Exclude self-counts
        
        # Ripley's K function formula
        k = (area * count) / (n_points * (n_points - 1))
        k_values[i] = k
        
        # L function (linearized K function)
        l_values[i] = np.sqrt(k / np.pi) - r
    
    return {
        "distances": np.array(distances),
        "k_function": k_values,
        "l_function": l_values
    }

def semivariogram(coords: np.ndarray, values: np.ndarray, lag_distances: List[float], 
                  tolerance: float = 0.5) -> Dict[str, np.ndarray]:
    """
    Calculate empirical semivariogram.
    
    Args:
        coords: Array of coordinates (n x 2)
        values: Array of values at each location
        lag_distances: List of lag distances at which to calculate semivariance
        tolerance: Tolerance for binning point pairs by distance
        
    Returns:
        Dictionary with semivariogram values
    """
    n_points = coords.shape[0]
    n_lags = len(lag_distances)
    
    # Initialize outputs
    semivariance = np.zeros(n_lags)
    count = np.zeros(n_lags, dtype=int)
    
    # Calculate semivariogram for each lag distance
    for i in range(n_points):
        for j in range(i+1, n_points):
            # Calculate Euclidean distance
            dist = np.sqrt(np.sum((coords[i] - coords[j])**2))
            
            # Find appropriate lag bin
            for k, lag in enumerate(lag_distances):
                if abs(dist - lag) <= tolerance:
                    # Calculate squared difference of values
                    sq_diff = (values[i] - values[j])**2
                    semivariance[k] += sq_diff
                    count[k] += 1
                    break
    
    # Calculate average semivariance for each lag
    valid_lags = count > 0
    semivariance[valid_lags] = semivariance[valid_lags] / (2 * count[valid_lags])
    
    return {
        "lag_distances": np.array(lag_distances),
        "semivariance": semivariance,
        "count": count
    }

def spatial_descriptive_statistics(coords: np.ndarray, values: np.ndarray) -> SpatialDescriptiveStats:
    """
    Calculate spatial descriptive statistics.
    
    Args:
        coords: Array of coordinates (n x 2)
        values: Array of values at each location
        
    Returns:
        SpatialDescriptiveStats object with calculated statistics
    """
    # Basic statistics
    mean_val = np.mean(values)
    median_val = np.median(values)
    std_val = np.std(values)
    var_val = np.var(values)
    min_val = np.min(values)
    max_val = np.max(values)
    
    # Calculate weighted centroid
    total_weight = np.sum(values)
    if total_weight > 0:
        centroid_x = np.sum(coords[:, 0] * values) / total_weight
        centroid_y = np.sum(coords[:, 1] * values) / total_weight
    else:
        # Unweighted centroid if values sum to zero
        centroid_x = np.mean(coords[:, 0])
        centroid_y = np.mean(coords[:, 1])
    
    # Spatial dispersion (average distance from centroid)
    centroid = np.array([centroid_x, centroid_y])
    distances = np.sqrt(np.sum((coords - centroid)**2, axis=1))
    dispersion = np.mean(distances)
    
    # Calculate skewness
    diff = values - mean_val
    skewness = np.sum(diff**3) / (len(values) * std_val**3)
    
    # Calculate kurtosis
    kurtosis = np.sum(diff**4) / (len(values) * std_val**4) - 3
    
    return SpatialDescriptiveStats(
        mean=mean_val,
        median=median_val,
        stdev=std_val,
        variance=var_val,
        min_value=min_val,
        max_value=max_val,
        centroid=(centroid_x, centroid_y),
        dispersion=dispersion,
        skewness=skewness,
        kurtosis=kurtosis
    )

def spatial_entropy(values: np.ndarray, bins: int = 10) -> float:
    """
    Calculate spatial entropy of a distribution.
    
    Args:
        values: Array of values
        bins: Number of bins for histogram
        
    Returns:
        Entropy value
    """
    # Create histogram
    hist, _ = np.histogram(values, bins=bins, density=True)
    
    # Filter out zeros
    hist = hist[hist > 0]
    
    # Calculate entropy
    entropy = -np.sum(hist * np.log(hist))
    
    return entropy

def local_indicators_spatial_association(
    values: np.ndarray, 
    weights_matrix: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Calculate Local Indicators of Spatial Association (LISA).
    
    Args:
        values: Array of values at each location
        weights_matrix: Spatial weights matrix
        
    Returns:
        Dictionary with LISA statistics for each location
    """
    n = len(values)
    z = (values - np.mean(values)) / np.std(values)
    
    # Calculate local Moran's I for each location
    lisa = np.zeros(n)
    expected_i = -1.0 / (n - 1)
    var_i = np.zeros(n)
    z_scores = np.zeros(n)
    p_values = np.zeros(n)
    
    for i in range(n):
        # Local Moran's I
        w_i = weights_matrix[i]
        sum_w = np.sum(w_i)
        
        if sum_w > 0:
            # Standardize weights
            w_std = w_i / sum_w
            
            # Calculate local Moran's I
            lisa[i] = z[i] * np.sum(w_std * z)
            
            # Calculate variance for significance testing
            b2 = np.sum(z**4) / n
            s1 = np.sum(w_std**2)
            
            # Simplified variance formula
            var_i[i] = s1 * (n - b2) / (n - 1)
            
            # Z-score and p-value
            z_scores[i] = (lisa[i] - expected_i) / np.sqrt(var_i[i])
            p_values[i] = 2 * (1 - np.abs(np.clip(z_scores[i], -8, 8) / 8))
    
    # Classify into High-High, Low-Low, High-Low, Low-High
    classifications = np.zeros(n, dtype=int)
    significant = p_values <= 0.05
    
    for i in range(n):
        if not significant[i]:
            continue
            
        if z[i] > 0:
            if lisa[i] > 0:
                classifications[i] = 1  # High-High
            else:
                classifications[i] = 3  # High-Low
        else:
            if lisa[i] > 0:
                classifications[i] = 2  # Low-Low
            else:
                classifications[i] = 4  # Low-High
    
    return {
        "lisa": lisa,
        "z_scores": z_scores,
        "p_values": p_values,
        "classifications": classifications,
        "significant": significant
    }

__all__ = [
    "SpatialDescriptiveStats",
    "MoranI",
    "getis_ord_g",
    "ripley_k",
    "semivariogram",
    "spatial_descriptive_statistics",
    "spatial_entropy",
    "local_indicators_spatial_association"
] 