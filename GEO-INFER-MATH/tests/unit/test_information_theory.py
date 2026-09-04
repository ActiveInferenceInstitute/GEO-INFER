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


def test_channel_capacity_noiseless_bsc():
    """Blahut-Arimoto capacity of a noiseless n-input channel is log2(n)."""
    from geo_infer_math.core.information_theory.channel_capacity import channel_capacity

    for n in (2, 4, 8):
        capacity = channel_capacity(np.eye(n))
        assert abs(capacity - np.log2(n)) < 1e-6


def test_channel_capacity_symmetric_bsc():
    """BA capacity of a symmetric BSC matches the analytic value."""
    from geo_infer_math.core.information_theory.channel_capacity import channel_capacity

    eps = 0.1
    bsc = np.array([[1 - eps, eps], [eps, 1 - eps]])
    capacity = channel_capacity(bsc)
    analytic = 1.0 - (-(eps * np.log2(eps) + (1 - eps) * np.log2(1 - eps)))
    assert abs(capacity - analytic) < 1e-4

