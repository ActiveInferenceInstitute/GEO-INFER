"""
GEO-INFER-SPM: Statistical Parametric Mapping for Geospatial Analysis

This module implements Statistical Parametric Mapping (SPM) methodology adapted
for geospatial analysis, providing rigorous statistical inference for spatially
and temporally continuous data fields while preserving spatiotemporal relationships.

The implementation is grounded in Active Inference principles, using Bayesian
inference for uncertainty quantification and free energy minimization for
optimal model selection.

Core Components:
- General Linear Model (GLM) for geospatial data analysis
- Random Field Theory (RFT) for multiple comparison correction
- Spatial autocorrelation modeling and cluster-based inference
- Bayesian extensions with hierarchical models
- Comprehensive visualization and statistical mapping tools

Example:
    >>> import geo_infer_spm as gispm
    >>> # Load geospatial data
    >>> data = gispm.load_data("temperature_data.tif")
    >>> # Create design matrix
    >>> design = gispm.design_matrix(factors=[("season", ["winter", "spring"])])
    >>> # Fit GLM and compute SPM
    >>> model = gispm.fit_glm(data, design)
    >>> contrast = gispm.contrast(model, "spring > winter")
    >>> spm_map = gispm.compute_spm(model, contrast, correction="RFT")
"""

# Core SPM functionality
from .core.glm import GeneralLinearModel, fit_glm
from .core.rft import RandomFieldTheory, compute_spm
from .core.contrasts import Contrast, contrast

# Analysis tools (may have optional dependencies)
try:
    from .core.spatial_analysis import SpatialAnalyzer
except ImportError:
    SpatialAnalyzer = None

try:
    from .core.temporal_analysis import TemporalAnalyzer
except ImportError:
    TemporalAnalyzer = None

try:
    from .core.bayesian import BayesianSPM
except ImportError:
    BayesianSPM = None

# Data models
from .models.data_models import SPMData, SPMResult, ContrastResult

# Utilities
from .utils.data_io import load_data, save_spm
from .utils.helpers import create_design_matrix, generate_synthetic_data

# Visualization (may have optional dependencies)
try:
    from .utils.visualization import visualize_spm, create_statistical_map
except ImportError:
    visualize_spm = create_statistical_map = None

# API
from .api.endpoints import SPMAPI

__version__ = "1.0.0"
__author__ = "GEO-INFER Framework"
__description__ = "Statistical Parametric Mapping for Geospatial Analysis"

# Make version accessible as module attribute
VERSION = __version__

__all__ = [
    # Core SPM functionality
    "GeneralLinearModel",
    "fit_glm",
    "RandomFieldTheory",
    "compute_spm",
    "Contrast",
    "contrast",

    # Analysis tools
    "SpatialAnalyzer",
    "TemporalAnalyzer",
    "BayesianSPM",

    # Data models
    "SPMData",
    "SPMResult",
    "ContrastResult",

    # Utilities
    "load_data",
    "save_spm",
    "create_design_matrix",
    "generate_synthetic_data",
    "visualize_spm",
    "create_statistical_map",

    # API
    "SPMAPI"
]
