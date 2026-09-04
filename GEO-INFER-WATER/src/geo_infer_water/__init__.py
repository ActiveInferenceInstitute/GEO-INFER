"""GEO-INFER-WATER: Water Resources Management Module."""

__version__ = "0.2.0"
__author__ = "GEO-INFER Development Team"

from .core.hydrology import HydrologicalModeler
from .core.watershed import WatershedAnalyzer
from .core.water_quality import WaterQualityAssessor
from .core.water_infrastructure import WaterInfrastructurePlanner
from .core.flood_drought import FloodDroughtAnalyzer
from .core.watershed_delineation import WatershedDelineator
from .core.water_balance import WaterBalanceModeler

__all__ = [
    "HydrologicalModeler",
    "WatershedAnalyzer",
    "WaterQualityAssessor",
    "WaterInfrastructurePlanner",
    "FloodDroughtAnalyzer",
    "WatershedDelineator",
    "WaterBalanceModeler",
]
