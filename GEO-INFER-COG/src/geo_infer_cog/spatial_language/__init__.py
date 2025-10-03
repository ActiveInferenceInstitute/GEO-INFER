"""
Spatial Language Processing for GEO-INFER-COG

This module provides natural language processing capabilities for geographic
and spatial content, enabling extraction of spatial information from text
and understanding of spatial language in human communication.

Available Components:
- Spatial Language Processor: Main NLP engine for spatial content
- Spatial Entity Extractor: Geographic named entity recognition
- Spatial Relation Extractor: Spatial relationship identification
- Place Description Interpreter: Text-based location understanding

Integration Points:
- GEO-INFER-DATA: Text data processing and extraction
- GEO-INFER-SPACE: Spatial data integration and geocoding
- GEO-INFER-APP: Natural language interfaces for geospatial tools
"""

from .processor import (
    SpatialLanguageProcessor,
    SpatialEntity,
    SpatialRelation
)

__all__ = [
    "SpatialLanguageProcessor",
    "SpatialEntity",
    "SpatialRelation"
]
