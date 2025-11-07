"""
Tests for Convenience API
"""

import numpy as np
import pytest
from geo_infer_math.api.convenience import (
    ActiveInferenceConvenience,
    BayesianConvenience,
    AIConvenience,
)

def test_act_convenience():
    """Test Active Inference convenience."""
    conv = ActiveInferenceConvenience()
    observations = np.random.rand(10)
    beliefs = np.ones(5) / 5
    
    free_energy = conv.calculate_free_energy(observations, beliefs)
    assert np.isfinite(free_energy)

def test_bayes_convenience():
    """Test Bayesian convenience."""
    conv = BayesianConvenience()
    prior = conv.build_prior('uniform', size=10)
    assert len(prior) == 10
    assert np.isclose(np.sum(prior), 1.0)

def test_ai_convenience():
    """Test AI convenience."""
    conv = AIConvenience()
    
    def objective(x):
        return np.sum(x ** 2)
    
    initial = np.array([1.0, 2.0])
    gradient = conv.compute_gradient(objective, initial)
    assert len(gradient) == len(initial)

