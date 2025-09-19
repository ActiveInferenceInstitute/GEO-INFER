"""
Utility functions for GEO-INFER-SPM

This module contains utility functions for data input/output, preprocessing,
validation, and helper functions used throughout the SPM package.
"""

from .data_io import load_data, save_spm, load_geospatial_data
from .preprocessing import preprocess_data, normalize_data, handle_missing_data
from .validation import validate_spm_data, validate_design_matrix
from .helpers import create_design_matrix, generate_coordinates

__all__ = [
    "load_data",
    "save_spm",
    "load_geospatial_data",
    "preprocess_data",
    "normalize_data",
    "handle_missing_data",
    "validate_spm_data",
    "validate_design_matrix",
    "create_design_matrix",
    "generate_coordinates"
]
