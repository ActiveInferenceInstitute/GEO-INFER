"""Policy optimization for Active Inference."""
import numpy as np
from geo_infer_math.core.optimization import Optimizer

class PolicyOptimization:
    """Policy optimization for Active Inference."""
    def optimize_policy(self, policy_function, initial_policy, **kwargs):
        optimizer = Optimizer()
        return optimizer.optimize(policy_function, initial_policy, **kwargs)

