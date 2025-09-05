"""
Data models module for GEO-INFER-SPACE.

This module provides Pydantic data models for spatial data structures,
configuration schemas, and API request/response validation.
"""

from .data_models import (
    SpatialDataset,
    GeometryModel,
    CoordinateReferenceSystem,
    SpatialIndex,
    AnalysisResult,
    SpatialMetadata
)

from .config_models import (
    SpaceConfig,
    AnalysisConfig,
    IndexingConfig,
    APIConfig,
    DatabaseConfig
)

__all__ = [
    # Data models
    'SpatialDataset',
    'GeometryModel', 
    'CoordinateReferenceSystem',
    'SpatialIndex',
    'AnalysisResult',
    'SpatialMetadata',
    
    # Configuration models
    'SpaceConfig',
    'AnalysisConfig',
    'IndexingConfig',
    'APIConfig',
    'DatabaseConfig'
]
