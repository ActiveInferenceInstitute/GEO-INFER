"""Posterior distribution helpers."""
import numpy as np
from geo_infer_math.api.convenience.bayes_convenience import posterior_helper

class PosteriorHelpers:
    """Posterior distribution helpers."""
    def calculate_posterior(self, prior, likelihood, data, **kwargs):
        return posterior_helper(prior, likelihood, data, **kwargs)

