"""
Convenience API Examples

Examples demonstrating convenience API usage.
"""

import numpy as np
from geo_infer_math.api.convenience import (
    ActiveInferenceConvenience,
    BayesianConvenience,
    AIConvenience,
)

def example_act_convenience():
    """Example: Active Inference convenience methods."""
    conv = ActiveInferenceConvenience()
    
    observations = np.random.rand(10)
    beliefs = np.ones(5) / 5
    
    free_energy = conv.calculate_free_energy(observations, beliefs)
    print(f"Free energy: {free_energy:.4f}")
    
    return free_energy

def example_bayes_convenience():
    """Example: Bayesian convenience methods."""
    conv = BayesianConvenience()
    
    prior = conv.build_prior('uniform', size=10)
    print(f"Prior distribution shape: {prior.shape}")
    
    return prior

def example_ai_convenience():
    """Example: AI convenience methods."""
    conv = AIConvenience()
    
    def objective(x):
        return np.sum(x ** 2)
    
    initial = np.array([1.0, 2.0, 3.0])
    gradient = conv.compute_gradient(objective, initial)
    print(f"Gradient: {gradient}")
    
    return gradient

if __name__ == "__main__":
    print("Convenience API Examples")
    print("=" * 50)
    example_act_convenience()
    example_bayes_convenience()
    example_ai_convenience()

