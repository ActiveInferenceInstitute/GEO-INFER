"""Enhanced tensor operations for AI models."""
import numpy as np
from geo_infer_math.core.linalg_tensor import TensorOperations

class TensorOperations:
    """Enhanced tensor operations for AI models."""
    def __init__(self):
        self.tensor_ops = TensorOperations()
    def spatial_tensor_operation(self, tensor, operation, **kwargs):
        return getattr(self.tensor_ops, operation)(tensor, **kwargs)

