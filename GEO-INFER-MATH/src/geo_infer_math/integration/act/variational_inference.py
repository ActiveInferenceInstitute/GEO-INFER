"""Variational inference helpers for Active Inference."""
import numpy as np
from geo_infer_math.api.convenience.act_convenience import variational_inference_helper

class VariationalInferenceHelpers:
    """Variational inference helpers."""
    def perform_vi(self, observations, prior, **kwargs):
        return variational_inference_helper(observations, prior, **kwargs)

