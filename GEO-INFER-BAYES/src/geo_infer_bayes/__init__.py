"""
GEO-INFER-BAYES: Bayesian inference for geospatial applications
======================================================================

This module provides a comprehensive framework for Bayesian inference
processes within the GEO-INFER ecosystem, implementing probabilistic modeling,
uncertainty quantification, and Bayesian computational methods for geospatial
applications.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Team"
__email__ = "geo-infer@activeinference.institute"

# Import main submodules with error handling
try:
from . import api
except ImportError as e:
    api = None
    import logging
    logging.warning(f"BAYES API module not available: {e}")

try:
from . import core
except ImportError as e:
    core = None
    import logging
    logging.warning(f"BAYES core module not available: {e}")

try:
from . import models
except ImportError as e:
    models = None
    import logging
    logging.warning(f"BAYES models module not available: {e}")

try:
from . import utils
except ImportError as e:
    utils = None
    import logging
    logging.warning(f"BAYES utils module not available: {e}")

# Expose key classes for easy import with error handling
try:
from .models.spatial_gp import SpatialGP
except ImportError:
    SpatialGP = None

try:
from .core.inference import BayesianInference
except ImportError:
    BayesianInference = None

try:
from .core.posterior import PosteriorAnalysis 
except ImportError:
    PosteriorAnalysis = None

# High-level convenience class
class GaussianProcess:
    """
    High-level Gaussian Process interface for geospatial applications.
    
    Provides a simplified interface for spatial Gaussian process modeling
    with automatic handling of geospatial data structures.
    """
    
    def __init__(self, kernel_type='rbf', spatial_resolution=0.1):
        self.kernel_type = kernel_type
        self.spatial_resolution = spatial_resolution
        self.model = None
        
    def fit(self, X, y, **kwargs):
        """Fit the Gaussian process model."""
        # Implementation would use appropriate backend (PyMC, Stan, etc.)
        pass
        
    def predict(self, X_new, return_std=True):
        """Make predictions with uncertainty quantification."""
        # Implementation would return predictions and uncertainties
        pass

__all__ = [
    'SpatialGP',
    'BayesianInference', 
    'PosteriorAnalysis',
    'GaussianProcess'
] 