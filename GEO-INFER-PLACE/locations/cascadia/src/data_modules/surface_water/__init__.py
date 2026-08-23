"""
Cascadian Surface Water Module

Analyzes surface water resources and high-resolution hydrography using USGS
National Hydrography Dataset (NHD / NHDPlus HR) with topology traversal and validation.
"""

from .data_sources import CascadianSurfaceWaterDataSources
from .flowline_network import CascadiaFlowlineNetwork, FlowlineTopologyValidator

try:
    from .geo_infer_surface_water import GeoInferSurfaceWater
except ImportError:
    GeoInferSurfaceWater = None  # type: ignore[assignment, misc]

__all__ = [
    "CascadianSurfaceWaterDataSources",
    "CascadiaFlowlineNetwork",
    "FlowlineTopologyValidator",
    "GeoInferSurfaceWater",
]
