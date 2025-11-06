"""
GEO-INFER-CLIMATE: Climate Modeling and Analysis Module

This module provides comprehensive climate modeling, weather analysis, and climate change
impact assessment capabilities for geospatial systems.

Key Features:
- Climate data processing (CMIP, reanalysis datasets)
- Climate indices calculation (SPI, PDSI, heat indices)
- Statistical and dynamical downscaling methods
- Climate change projections and scenario analysis
- Extreme weather event analysis
- Climate impact assessment
- Climate adaptation planning tools
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

from .core.climate_data import ClimateDataProcessor
from .core.climate_indices import ClimateIndicesCalculator
from .core.downscaling import DownscalingMethods
from .core.projections import ClimateProjections
from .core.extreme_events import ExtremeEventAnalyzer
from .core.impact_assessment import ClimateImpactAssessor

__all__ = [
    "ClimateDataProcessor",
    "ClimateIndicesCalculator",
    "DownscalingMethods",
    "ClimateProjections",
    "ExtremeEventAnalyzer",
    "ClimateImpactAssessor",
]

