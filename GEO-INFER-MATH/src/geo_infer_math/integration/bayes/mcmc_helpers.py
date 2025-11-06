"""MCMC algorithm mathematical foundations."""
import numpy as np
from geo_infer_math.api.convenience.bayes_convenience import mcmc_wrapper

class MCMCHelpers:
    """MCMC algorithm helpers."""
    def mcmc_sample(self, log_posterior, initial_state, **kwargs):
        return mcmc_wrapper(log_posterior, initial_state, **kwargs)

