"""
Tests for Information Theory Module
"""

import numpy as np
import pytest
from geo_infer_math.core.information_theory import (
    shannon_entropy,
    renyi_entropy,
    spatial_entropy,
    mutual_information,
    kl_divergence,
)

def test_shannon_entropy():
    """Test Shannon entropy calculation."""
    # Uniform distribution should have maximum entropy
    uniform = np.ones(10) / 10
    entropy = shannon_entropy(uniform)
    assert entropy > 0
    assert entropy <= np.log2(10)

def test_spatial_entropy():
    """Test spatial entropy calculation."""
    coordinates = np.random.rand(50, 2) * 100
    values = np.random.rand(50)
    
    entropy = spatial_entropy(coordinates, values)
    assert entropy >= 0

def test_kl_divergence():
    """Test KL divergence calculation."""
    p = np.array([0.5, 0.5])
    q = np.array([0.3, 0.7])
    
    kl = kl_divergence(p, q)
    assert kl >= 0
    assert np.isfinite(kl)

