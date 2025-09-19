"""
Data models for GEO-INFER-SPM

This module contains data structures and models used throughout the SPM package
for representing geospatial data, statistical results, and analysis parameters.
"""

from .data_models import SPMData, SPMResult, ContrastResult, DesignMatrix

__all__ = [
    "SPMData",
    "SPMResult",
    "ContrastResult",
    "DesignMatrix"
]
