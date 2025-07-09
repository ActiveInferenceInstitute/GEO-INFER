"""
Data models and schemas for GEO-INFER-PLACE

This package contains data models, schemas, and result classes for 
place-based geospatial analysis.
"""

from .location import Location, LocationMetadata
from .analysis_result import AnalysisResult, PlaceBasedResult

__all__ = [
    "Location",
    "LocationMetadata",
    "AnalysisResult", 
    "PlaceBasedResult"
] 