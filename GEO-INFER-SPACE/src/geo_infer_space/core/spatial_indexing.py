"""
Generic spatial indexing interface for GEO-INFER-SPACE.

This module defines the generic interface for spatial indexing operations
that can be implemented by different backends (H3, SRAI, etc.).
"""

from typing import Dict, Any, List, Optional, Protocol, Union
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class SpatialIndexingInterface:
    """
    Generic interface for spatial indexing operations.

    This class provides a unified API for spatial indexing that can dispatch
    to different backends based on configuration.
    """

    def __init__(self, backend: Optional[str] = None):
        from .dispatcher import get_backend_dispatcher
        self.dispatcher = get_backend_dispatcher()
        self.backend = backend

    def latlng_to_cell(self, lat: float, lng: float, resolution: int) -> str:
        """
        Convert latitude/longitude coordinates to a spatial index cell.

        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            resolution: Resolution level for the spatial index

        Returns:
            Spatial index cell identifier
        """
        return self.dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', lat, lng, resolution, backend=self.backend
        )

    def cell_to_latlng(self, cell: str) -> tuple[float, float]:
        """
        Convert a spatial index cell back to latitude/longitude coordinates.

        Args:
            cell: Spatial index cell identifier

        Returns:
            Tuple of (latitude, longitude) coordinates
        """
        return self.dispatcher.dispatch_indexing_operation(
            'cell_to_latlng', cell, backend=self.backend
        )

    def polygon_to_cells(self, polygon: Dict[str, Any], resolution: int) -> List[str]:
        """
        Convert a polygon geometry to a list of spatial index cells.

        Args:
            polygon: Polygon geometry as GeoJSON-like dictionary
            resolution: Resolution level for the spatial index

        Returns:
            List of spatial index cell identifiers covering the polygon
        """
        return self.dispatcher.dispatch_indexing_operation(
            'polygon_to_cells', polygon, resolution, backend=self.backend
        )

    def get_cell_neighbors(self, cell: str, k: int = 1) -> List[str]:
        """
        Get neighboring cells around a given cell.

        Args:
            cell: Central spatial index cell
            k: Number of rings of neighbors to return

        Returns:
            List of neighboring cell identifiers
        """
        # This would need to be implemented by specific backends
        # For now, dispatch to a generic operation
        return self.dispatcher.dispatch_indexing_operation(
            'get_neighbors', cell, k, backend=self.backend
        )

    def get_cell_distance(self, cell1: str, cell2: str) -> int:
        """
        Calculate the distance between two spatial index cells.

        Args:
            cell1: First spatial index cell
            cell2: Second spatial index cell

        Returns:
            Distance between cells in grid units
        """
        return self.dispatcher.dispatch_indexing_operation(
            'get_distance', cell1, cell2, backend=self.backend
        )

    def compact_cells(self, cells: List[str]) -> List[str]:
        """
        Compact a list of cells into a more efficient representation.

        Args:
            cells: List of spatial index cell identifiers

        Returns:
            Compacted list of cell identifiers
        """
        return self.dispatcher.dispatch_indexing_operation(
            'compact_cells', cells, backend=self.backend
        )

    def uncompact_cells(self, compacted_cells: List[str], resolution: int) -> List[str]:
        """
        Uncompact cells back to individual cell identifiers.

        Args:
            compacted_cells: Compacted cell identifiers
            resolution: Target resolution level

        Returns:
            List of individual cell identifiers
        """
        return self.dispatcher.dispatch_indexing_operation(
            'uncompact_cells', compacted_cells, resolution, backend=self.backend
        )


# Convenience functions that use the default backend
def latlng_to_cell(lat: float, lng: float, resolution: int, backend: Optional[str] = None) -> str:
    """Convert lat/lng to cell using specified or default backend."""
    indexer = SpatialIndexingInterface(backend)
    return indexer.latlng_to_cell(lat, lng, resolution)


def cell_to_latlng(cell: str, backend: Optional[str] = None) -> tuple[float, float]:
    """Convert cell to lat/lng using specified or default backend."""
    indexer = SpatialIndexingInterface(backend)
    return indexer.cell_to_latlng(cell)


def polygon_to_cells(polygon: Dict[str, Any], resolution: int, backend: Optional[str] = None) -> List[str]:
    """Convert polygon to cells using specified or default backend."""
    indexer = SpatialIndexingInterface(backend)
    return indexer.polygon_to_cells(polygon, resolution)
