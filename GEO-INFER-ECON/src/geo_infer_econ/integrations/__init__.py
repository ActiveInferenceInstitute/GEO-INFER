"""
Integration adapters for GEO-INFER modules.

This module provides integration adapters for:
- GEO-INFER-SPACE: Spatial operations and indexing
- GEO-INFER-TIME: Temporal analysis and forecasting
- GEO-INFER-DATA: Data loading and management
"""

from .space_integration import SpaceIntegration
from .time_integration import TimeIntegration
from .data_integration import DataIntegration

__all__ = [
    'SpaceIntegration',
    'TimeIntegration',
    'DataIntegration',
]

