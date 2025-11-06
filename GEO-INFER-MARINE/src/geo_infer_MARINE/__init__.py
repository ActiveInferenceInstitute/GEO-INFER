"""
GEO-INFER-MARINE: Marine and Oceanographic Analysis Module

This module provides comprehensive marine and oceanographic analysis capabilities
including coastal management, marine ecosystem monitoring, and oceanographic data processing.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

from .core.oceanographic_data import OceanographicDataProcessor
from .core.coastal_analysis import CoastalAnalyzer
from .core.marine_ecosystems import MarineEcosystemModeler
from .core.sea_level import SeaLevelAnalyzer
from .core.marine_spatial_planning import MarineSpatialPlanner

__all__ = [
    "OceanographicDataProcessor",
    "CoastalAnalyzer",
    "MarineEcosystemModeler",
    "SeaLevelAnalyzer",
    "MarineSpatialPlanner",
]

