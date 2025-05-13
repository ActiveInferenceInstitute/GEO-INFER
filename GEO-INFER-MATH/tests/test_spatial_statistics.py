"""
Tests for the spatial_statistics module.
"""

import numpy as np
import pytest
from geo_infer_math.core.spatial_statistics import (
    MoranI, getis_ord_g, ripley_k, semivariogram, 
    spatial_descriptive_statistics, spatial_entropy,
    local_indicators_spatial_association
)

def test_moran_i():
    """Test Moran's I statistic calculation."""
    # Create a simple test case with positive spatial autocorrelation
    # (similar values are close to each other)
    values = np.array([10, 12, 11, 13, 50, 52, 51, 53])
    coords = np.array([
        [1, 1], [1, 2], [2, 1], [2, 2],  # Cluster of low values
        [10, 10], [10, 11], [11, 10], [11, 11]  # Cluster of high values
    ])
    
    # Calculate Moran's I
    moran = MoranI()
    result = moran.compute(values, coords)
    
    # With this pattern, we expect positive spatial autocorrelation
    assert result['I'] > 0
    
    # The expected I should be -1/(n-1) = -1/7 ≈ -0.143
    assert abs(result['expected_I'] - (-1/7)) < 1e-10
    
    # Check that the p-value is valid
    assert 0 <= result['p_value'] <= 1
    
    # Test with pre-defined weights matrix
    n = len(values)
    weights = np.zeros((n, n))
    
    # Define simple weights: adjacent points have weight 1
    for i in range(4):
        for j in range(4):
            if i != j and abs(coords[i, 0] - coords[j, 0]) <= 1 and abs(coords[i, 1] - coords[j, 1]) <= 1:
                weights[i, j] = 1
                
    for i in range(4, 8):
        for j in range(4, 8):
            if i != j and abs(coords[i, 0] - coords[j, 0]) <= 1 and abs(coords[i, 1] - coords[j, 1]) <= 1:
                weights[i, j] = 1
    
    # Row-standardize weights
    row_sums = weights.sum(axis=1)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    weights = weights / row_sums[:, np.newaxis]
    
    moran_with_weights = MoranI(weights)
    result_with_weights = moran_with_weights.compute(values)
    
    # We should still get positive spatial autocorrelation
    assert result_with_weights['I'] > 0

def test_getis_ord_g():
    """Test Getis-Ord G* statistic calculation."""
    # Create a test case with a hot spot and a cold spot
    values = np.array([10, 11, 12, 13, 50, 51, 52, 53])
    
    # Create a weights matrix
    n = len(values)
    weights = np.zeros((n, n))
    
    # Define simple binary weights for two distinct clusters
    for i in range(4):
        for j in range(4):
            if i != j:
                weights[i, j] = 1
                
    for i in range(4, 8):
        for j in range(4, 8):
            if i != j:
                weights[i, j] = 1
    
    # Row-standardize
    row_sums = weights.sum(axis=1)
    weights = weights / row_sums[:, np.newaxis]
    
    # Calculate Getis-Ord G*
    result = getis_ord_g(values, weights)
    
    # Check results
    assert 'local_g' in result
    assert 'z_scores' in result
    assert 'global_g' in result
    
    # The high values should be hot spots (positive z-scores)
    assert np.all(result['z_scores'][4:8] > 0)
    
    # The low values should be cold spots (negative z-scores)
    assert np.all(result['z_scores'][0:4] < 0)

def test_ripley_k():
    """Test Ripley's K function calculation."""
    # Create a simple point pattern
    points = np.array([
        [1, 1], [2, 2], [3, 3], [4, 4],  # Clustered along diagonal
        [10, 10], [11, 11], [12, 12], [13, 13]  # Another cluster
    ])
    
    # Define distances at which to evaluate K
    distances = [1, 2, 5, 10, 15]
    
    # Area (assuming a 20x20 study area)
    area = 400
    
    # Calculate Ripley's K
    result = ripley_k(points, distances, area)
    
    # Check results
    assert 'distances' in result
    assert 'k_function' in result
    assert 'l_function' in result
    
    # K should increase with distance
    assert np.all(np.diff(result['k_function']) >= 0)
    
    # For a clustered pattern, the L function should be positive at smaller distances
    assert result['l_function'][0] > 0 or result['l_function'][1] > 0

def test_semivariogram():
    """Test semivariogram calculation."""
    # Create a simple dataset with spatial structure
    coords = np.array([
        [0, 0], [1, 0], [2, 0], [3, 0], [4, 0],
        [0, 1], [1, 1], [2, 1], [3, 1], [4, 1]
    ])
    
    # Values with spatial trend (increasing from bottom-left to top-right)
    values = np.array([1, 2, 3, 4, 5, 2, 3, 4, 5, 6])
    
    # Lag distances
    lag_distances = [1, 2, 3, 4, 5]
    
    # Calculate semivariogram
    result = semivariogram(coords, values, lag_distances)
    
    # Check results
    assert 'lag_distances' in result
    assert 'semivariance' in result
    assert 'count' in result
    
    # For this dataset, semivariance should generally increase with distance
    # (but might not be strictly increasing due to sampling variability)
    assert result['semivariance'][0] < result['semivariance'][-1]

def test_spatial_descriptive_statistics():
    """Test spatial descriptive statistics calculation."""
    # Create test data
    coords = np.array([
        [0, 0], [1, 0], [0, 1], [1, 1]
    ])
    values = np.array([10, 20, 30, 40])
    
    # Calculate statistics
    stats = spatial_descriptive_statistics(coords, values)
    
    # Check basic statistics
    assert stats.mean == 25.0
    assert stats.median == 25.0
    assert abs(stats.stdev - np.std(values, ddof=0)) < 1e-10
    assert abs(stats.variance - np.var(values, ddof=0)) < 1e-10
    assert stats.min_value == 10.0
    assert stats.max_value == 40.0
    
    # Check centroid
    # For this example, the weighted centroid should be biased towards higher values
    assert stats.centroid[0] > 0.5
    assert stats.centroid[1] > 0.5

def test_spatial_entropy():
    """Test spatial entropy calculation."""
    # Test with uniform distribution
    uniform = np.ones(100)
    entropy_uniform = spatial_entropy(uniform)
    
    # Test with concentrated distribution
    concentrated = np.zeros(100)
    concentrated[45:55] = 1.0
    entropy_concentrated = spatial_entropy(concentrated)
    
    # Entropy should be higher for uniform distribution
    assert entropy_uniform > entropy_concentrated
    
    # Test with different number of bins
    entropy_10_bins = spatial_entropy(uniform, bins=10)
    entropy_20_bins = spatial_entropy(uniform, bins=20)
    
    # More bins should generally increase entropy for uniform distribution
    assert entropy_20_bins >= entropy_10_bins

def test_local_indicators_spatial_association():
    """Test LISA calculation."""
    # Create a simple test case with spatial pattern
    values = np.array([10, 12, 11, 13, 50, 52, 51, 53])
    
    # Create a weights matrix
    n = len(values)
    weights = np.zeros((n, n))
    
    # Define weights for two distinct clusters
    for i in range(4):
        for j in range(4):
            if i != j:
                weights[i, j] = 1
                
    for i in range(4, 8):
        for j in range(4, 8):
            if i != j:
                weights[i, j] = 1
    
    # Row-standardize
    row_sums = weights.sum(axis=1)
    weights = weights / row_sums[:, np.newaxis]
    
    # Calculate LISA
    result = local_indicators_spatial_association(values, weights)
    
    # Check results
    assert 'lisa' in result
    assert 'z_scores' in result
    assert 'p_values' in result
    assert 'classifications' in result
    
    # Check classifications
    # The clusters should be classified as High-High or Low-Low
    high_vals = values > np.mean(values)
    
    for i in range(n):
        if result['significant'][i]:
            if high_vals[i]:
                # High values should be in High-High clusters
                assert result['classifications'][i] == 1
            else:
                # Low values should be in Low-Low clusters
                assert result['classifications'][i] == 2 