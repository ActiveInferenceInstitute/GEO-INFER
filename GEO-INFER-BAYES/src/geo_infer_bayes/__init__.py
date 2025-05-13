"""
GEO-INFER-BAYES: Bayesian inference for geospatial applications
======================================================================

This module provides a comprehensive framework for Bayesian inference
processes within the GEO-INFER ecosystem, implementing probabilistic modeling,
uncertainty quantification, and Bayesian computational methods for geospatial
applications.
"""

__version__ = "0.1.0"

# Import main submodules
from . import api
from . import core
from . import models
from . import utils

# Expose key classes for easy import
from .models.spatial_gp import SpatialGP
from .core.inference import BayesianInference
from .core.posterior import PosteriorAnalysis 