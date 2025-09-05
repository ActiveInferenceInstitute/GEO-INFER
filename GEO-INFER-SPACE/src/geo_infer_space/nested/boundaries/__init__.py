"""
Boundary Management for Nested Systems.

This module provides comprehensive boundary detection, analysis, and management
capabilities for nested geospatial systems using H3 hexagonal grids.
"""

from .detector import BoundaryDetector, BoundaryType, BoundarySegment
from .boundary_manager import H3BoundaryManager

__all__ = [
    'BoundaryDetector',
    'H3BoundaryManager',
    'BoundaryType',
    'BoundarySegment'
]
