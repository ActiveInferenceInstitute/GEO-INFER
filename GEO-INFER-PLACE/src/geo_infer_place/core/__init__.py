"""
Core analysis modules for GEO-INFER-PLACE

Contains the core analytical components for place-based geospatial analysis:
- BaseAnalysisModule: Abstract base for domain-specific analyzers
- CascadianAgriculturalH3Backend: H3-indexed Cascadia backend
- InteractiveVisualizationEngine: Dashboard and map generation
- PlaceInterface: Unified entry point for all analyses
- PlaceDataManager: GEO-INFER-DATA quality and provenance bridge
- PlaceTemporalAnalyzer: GEO-INFER-TIME trend and anomaly bridge
"""

from .base_module import BaseAnalysisModule
from .unified_backend import CascadianAgriculturalH3Backend
from .visualization_engine import InteractiveVisualizationEngine
from .place_interface import PlaceInterface
from .module_bridge import PlaceDataManager, PlaceTemporalAnalyzer

__all__ = [
    "BaseAnalysisModule",
    "CascadianAgriculturalH3Backend",
    "InteractiveVisualizationEngine",
    "PlaceInterface",
    "PlaceDataManager",
    "PlaceTemporalAnalyzer",
]
