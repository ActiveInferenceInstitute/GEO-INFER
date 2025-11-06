"""Prior distribution construction tools."""
import numpy as np
from geo_infer_math.api.convenience.bayes_convenience import prior_builder

class PriorBuilders:
    """Prior distribution construction tools."""
    def build_prior(self, distribution_type, **kwargs):
        return prior_builder(distribution_type, kwargs)

