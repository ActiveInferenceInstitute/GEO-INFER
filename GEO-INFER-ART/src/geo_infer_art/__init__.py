"""
GEO-INFER-ART: Art production and aesthetics with geospatial dimensions.

This module enables the transformation of geospatial data into artistic
expressions, visualizations, and generative art systems.
"""

__version__ = "0.1.0"

# Core components
from geo_infer_art.core.visualization import GeoArt
from geo_infer_art.core.aesthetics import StyleTransfer, ColorPalette
from geo_infer_art.core.generation import GenerativeMap, ProceduralArt
from geo_infer_art.core.place import PlaceArt, CulturalMap

# Expose key classes at package level
__all__ = [
    "GeoArt",
    "StyleTransfer",
    "ColorPalette",
    "GenerativeMap",
    "ProceduralArt",
    "PlaceArt",
    "CulturalMap",
]
