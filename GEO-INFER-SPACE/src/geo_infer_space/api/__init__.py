"""
API module for GEO-INFER-SPACE spatial services.

This module provides REST API endpoints for accessing spatial analysis
capabilities through FastAPI with automatic documentation generation.
"""

from .rest_api import app, router
from .schemas import (
    SpatialAnalysisRequest,
    SpatialAnalysisResponse,
    BufferAnalysisRequest,
    ProximityAnalysisRequest,
    InterpolationRequest,
    ClusteringRequest,
    HotspotRequest,
    NetworkAnalysisRequest,
    ErrorResponse
)

__all__ = [
    'app',
    'router',
    'SpatialAnalysisRequest',
    'SpatialAnalysisResponse', 
    'BufferAnalysisRequest',
    'ProximityAnalysisRequest',
    'InterpolationRequest',
    'ClusteringRequest',
    'HotspotRequest',
    'NetworkAnalysisRequest',
    'ErrorResponse'
]
