"""Spatial loss functions for neural networks."""
import numpy as np
from typing import Optional
from geo_infer_math.api.convenience.ai_convenience import spatial_loss_function

class SpatialLossFunctions:
    """Spatial loss functions for neural networks."""
    def calculate_loss(self, predictions, targets, coordinates=None, **kwargs):
        return spatial_loss_function(predictions, targets, coordinates, **kwargs)

