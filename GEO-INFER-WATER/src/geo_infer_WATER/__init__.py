"""
GEO-INFER-WATER: Water Resources Management Module
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

from .core.hydrology import HydrologicalModeler
from .core.watershed import WatershedAnalyzer
from .core.water_quality import WaterQualityAssessor
from .core.water_infrastructure import WaterInfrastructurePlanner
from .core.flood_drought import FloodDroughtAnalyzer

__all__ = [
    "HydrologicalModeler",
    "WatershedAnalyzer",
    "WaterQualityAssessor",
    "WaterInfrastructurePlanner",
    "FloodDroughtAnalyzer",
]

