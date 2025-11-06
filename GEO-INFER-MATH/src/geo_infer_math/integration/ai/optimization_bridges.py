"""Bridge between MATH optimization and AI training."""
import numpy as np
from typing import Callable, Tuple, Dict
from geo_infer_math.api.convenience.ai_convenience import optimization_wrapper

class OptimizationBridges:
    """Bridge between MATH optimization and AI training."""
    def bridge_optimize(self, objective, initial_guess, **kwargs):
        return optimization_wrapper(objective, initial_guess, **kwargs)

