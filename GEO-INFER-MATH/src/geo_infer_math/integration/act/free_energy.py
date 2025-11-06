"""Free energy calculations for Active Inference."""
import numpy as np
from geo_infer_math.api.convenience.act_convenience import free_energy_calculation

class FreeEnergyCalculator:
    """Free energy calculations for Active Inference."""
    def calculate(self, observations, beliefs, **kwargs):
        return free_energy_calculation(observations, beliefs, **kwargs)

