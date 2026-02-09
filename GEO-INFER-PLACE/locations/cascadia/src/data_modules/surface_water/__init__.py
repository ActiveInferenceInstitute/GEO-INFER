"""
Cascadian Surface Water Module

Analyzes surface water resources using USGS National Hydrography Dataset.
"""

from .data_sources import CascadianSurfaceWaterDataSources
try:
    from .geo_infer_surface_water import GeoInferSurfaceWater
except ImportError:
    GeoInferSurfaceWater = None

__all__ = ["CascadianSurfaceWaterDataSources", "GeoInferSurfaceWater"]
