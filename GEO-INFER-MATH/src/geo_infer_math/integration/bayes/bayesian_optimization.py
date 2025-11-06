"""Bayesian optimization tools."""
import numpy as np
from geo_infer_math.api.convenience.bayes_convenience import bayesian_optimization_helper

class BayesianOptimization:
    """Bayesian optimization tools."""
    def optimize(self, objective, prior, **kwargs):
        return bayesian_optimization_helper(objective, prior, **kwargs)

