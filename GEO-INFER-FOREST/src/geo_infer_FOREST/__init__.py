"""
GEO-INFER-FOREST: Forest Management and Analysis Module
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

from .core.forest_inventory import ForestInventory
from .core.carbon_sequestration import CarbonSequestrationModeler
from .core.wildfire_risk import WildfireRiskAnalyzer
from .core.forest_health import ForestHealthMonitor

__all__ = [
    "ForestInventory",
    "CarbonSequestrationModeler",
    "WildfireRiskAnalyzer",
    "ForestHealthMonitor",
]

