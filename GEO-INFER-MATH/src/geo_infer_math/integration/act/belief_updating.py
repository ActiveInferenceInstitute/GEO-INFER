"""Belief updating for Active Inference."""
import numpy as np
from geo_infer_math.api.convenience.act_convenience import belief_updating_helper

class BeliefUpdating:
    """Belief updating for Active Inference."""
    def update(self, current_beliefs, new_observations, **kwargs):
        return belief_updating_helper(current_beliefs, new_observations, **kwargs)

