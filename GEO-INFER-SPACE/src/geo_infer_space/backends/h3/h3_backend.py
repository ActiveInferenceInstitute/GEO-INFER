"""
H3 Backend Implementation for GEO-INFER-SPACE.

This module provides the H3-specific implementation of spatial operations
that integrates with the generic spatial methods layer. All operations
require the H3 library to be installed - no mock implementations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from ...core.interfaces import (
    IndexingBackendProtocol,
    AnalyticsBackendProtocol,
    H3UnavailableError,
)

logger = logging.getLogger(__name__)


def _require_h3(operation: str):
    """Decorator to require H3 library for an operation."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not self._available:
                logger.error(f"H3 library required for {operation}")
                raise H3UnavailableError(operation)
            return func(self, *args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


class H3Backend:
    """
    H3 backend implementation for spatial operations.

    This class provides H3-specific implementations of the generic spatial
    interfaces. All operations require the H3 library - operations will
    raise H3UnavailableError if H3 is not installed.
    
    Implements: IndexingBackendProtocol, AnalyticsBackendProtocol
    """

    def __init__(self):
        """Initialize the H3 backend and check library availability."""
        self._check_h3_availability()

    def _check_h3_availability(self):
        """Check if H3 library is available."""
        try:
            import h3
            self.h3 = h3
            self._available = True
            logger.info(f"H3 library v{getattr(h3, '__version__', 'unknown')} loaded successfully")
        except ImportError:
            self.h3 = None
            self._available = False
            logger.warning("H3 library is not installed - install with: pip install h3")

    @property
    def name(self) -> str:
        """Return the backend name."""
        return "h3"

    @property
    def version(self) -> str:
        """Return the backend version."""
        if self.h3:
            return getattr(self.h3, '__version__', 'unknown')
        return "not-installed"

    def is_available(self) -> bool:
        """Check if the backend is available and functional."""
        return self._available

    def get_capabilities(self) -> Dict[str, Any]:
        """Return the backend's capabilities."""
        return {
            'indexing': {
                'latlng_to_cell': self._available,
                'cell_to_latlng': self._available,
                'polygon_to_cells': self._available,
                'get_neighbors': self._available,
                'get_distance': self._available,
                'compact_cells': self._available,
                'uncompact_cells': self._available,
            },
            'analytics': {
                'analyze_hotspots': self._available,
                'compute_proximity': self._available,
                'cluster_points': self._available,
                'interpolate_values': self._available,
            },
            'geometric': {
                'buffer_geometry': self._available,
                'calculate_area': self._available,
                'calculate_perimeter': self._available,
                'calculate_centroid': self._available,
                'union_geometries': self._available,
                'intersection_geometries': self._available,
                'difference_geometries': self._available,
            },
            'supported_resolutions': list(range(16)),  # H3 supports resolutions 0-15
            'coordinate_system': 'WGS84',
            'available': self._available,
        }

    # SpatialIndexingBackend implementation
    @_require_h3("latlng_to_cell")
    def latlng_to_cell(self, lat: float, lng: float, resolution: int) -> str:
        """
        Convert lat/lng coordinates to H3 cell.
        
        Args:
            lat: Latitude (-90 to 90)
            lng: Longitude (-180 to 180)
            resolution: H3 resolution (0-15)
            
        Returns:
            H3 cell identifier string
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If coordinates or resolution are invalid
        """
        logger.debug(f"Converting ({lat}, {lng}) to H3 cell at resolution {resolution}")
        return self.h3.latlng_to_cell(lat, lng, resolution)

    @_require_h3("cell_to_latlng")
    def cell_to_latlng(self, cell: str) -> tuple[float, float]:
        """
        Convert H3 cell back to lat/lng coordinates.
        
        Args:
            cell: H3 cell identifier
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cell identifier is invalid
        """
        logger.debug(f"Converting H3 cell {cell} to coordinates")
        return self.h3.cell_to_latlng(cell)

    @_require_h3("polygon_to_cells")
    def polygon_to_cells(self, polygon: Dict[str, Any], resolution: int) -> List[str]:
        """
        Convert polygon to list of H3 cells.
        
        Args:
            polygon: GeoJSON-like polygon dictionary with 'coordinates' key
            resolution: H3 resolution (0-15)
            
        Returns:
            List of H3 cell identifiers covering the polygon
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If polygon format is invalid
        """
        coords = polygon.get('coordinates', [])
        if not coords or not coords[0]:
            logger.warning("Empty polygon coordinates provided")
            return []
        
        # Convert GeoJSON [lng, lat] to H3 (lat, lng) format for LatLngPoly
        outer_ring = coords[0]
        h3_coords = [(point[1], point[0]) for point in outer_ring]  # swap from [lng, lat] to (lat, lng)
        
        try:
            from h3 import LatLngPoly
            logger.debug(f"Converting polygon with {len(h3_coords)} vertices to H3 cells at resolution {resolution}")
            h3_polygon = LatLngPoly(h3_coords)
            cells = list(self.h3.polygon_to_cells(h3_polygon, resolution))
            logger.debug(f"Generated {len(cells)} H3 cells from polygon")
            return cells
        except Exception as e:
            logger.warning(f"H3 polygon conversion failed: {e}")
            logger.debug("Falling back to manual boundary sampling")
            
            # Fallback for complex/invalid geometries: sample the boundary
            cells = set()
            for lng, lat in outer_ring:
                try:
                    cell = self.h3.latlng_to_cell(lat, lng, resolution)
                    cells.add(cell)
                except Exception:
                    continue
            return list(cells)

    @_require_h3("get_cell_neighbors")
    def get_cell_neighbors(self, cell: str, k: int = 1) -> List[str]:
        """
        Get neighboring cells around a given cell.
        
        Args:
            cell: Central H3 cell identifier
            k: Number of rings of neighbors (default 1)
            
        Returns:
            List of neighboring H3 cell identifiers
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cell identifier is invalid
        """
        logger.debug(f"Getting k={k} neighbors for cell {cell}")
        if k == 1:
            # For k=1, use grid_ring for efficiency
            return list(self.h3.grid_ring(cell, 1))
        else:
            # For k>1, use grid_disk and remove inner rings
            disk = set(self.h3.grid_disk(cell, k))
            inner_disk = set(self.h3.grid_disk(cell, k-1)) if k > 1 else {cell}
            return list(disk - inner_disk)

    @_require_h3("get_cell_distance")
    def get_cell_distance(self, cell1: str, cell2: str) -> int:
        """
        Calculate the grid distance between two H3 cells.
        
        Args:
            cell1: First H3 cell identifier
            cell2: Second H3 cell identifier
            
        Returns:
            Grid distance between cells
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cells are at different resolutions or invalid
        """
        logger.debug(f"Calculating distance between {cell1} and {cell2}")
        return self.h3.grid_distance(cell1, cell2)

    @_require_h3("compact_cells")
    def compact_cells(self, cells: List[str]) -> List[str]:
        """
        Compact a list of cells into a more efficient representation.
        
        Args:
            cells: List of H3 cell identifiers
            
        Returns:
            Compacted list of cell identifiers at mixed resolutions
            
        Raises:
            H3UnavailableError: If H3 library is not installed
        """
        logger.debug(f"Compacting {len(cells)} cells")
        result = list(self.h3.compact_cells(cells))
        logger.debug(f"Compacted to {len(result)} cells")
        return result

    @_require_h3("uncompact_cells")
    def uncompact_cells(self, compacted_cells: List[str], resolution: int) -> List[str]:
        """
        Uncompact cells back to individual cell identifiers.
        
        Args:
            compacted_cells: Compacted cell identifiers
            resolution: Target resolution level
            
        Returns:
            List of individual cell identifiers at target resolution
            
        Raises:
            H3UnavailableError: If H3 library is not installed
        """
        logger.debug(f"Uncompacting {len(compacted_cells)} cells to resolution {resolution}")
        result = list(self.h3.uncompact_cells(compacted_cells, resolution))
        logger.debug(f"Uncompacted to {len(result)} cells")
        return result

    @_require_h3("get_cell_parent")
    def get_cell_parent(self, cell: str, resolution: int) -> str:
        """
        Get the parent of a cell at a coarser resolution.
        
        Args:
            cell: H3 cell identifier
            resolution: Target resolution
            
        Returns:
            Parent cell identifier
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If resolutions are incompatible
        """
        logger.debug(f"Getting parent of {cell} at resolution {resolution}")
        try:
            return self.h3.cell_to_parent(cell, resolution)
        except Exception as e:
            raise ValueError(f"Failed to get parent: {e}") from e

    @_require_h3("get_cell_children")
    def get_cell_children(self, cell: str, resolution: int) -> List[str]:
        """
        Get children of a cell at a finer resolution.
        
        Args:
            cell: H3 cell identifier
            resolution: Target resolution
            
        Returns:
            List of child cell identifiers
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If resolutions are incompatible
        """
        logger.debug(f"Getting children of {cell} at resolution {resolution}")
        try:
            return list(self.h3.cell_to_children(cell, resolution))
        except Exception as e:
            raise ValueError(f"Failed to get children: {e}") from e

    @_require_h3("get_cell_path")
    def get_cell_path(self, start_cell: str, end_cell: str) -> List[str]:
        """
        Get the path of cells between two cells.
        
        Args:
            start_cell: Start cell identifier
            end_cell: End cell identifier
            
        Returns:
            List of cell identifiers in the path (inclusive)
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cells are invalid or disconnected
        """
        logger.debug(f"Calculating path from {start_cell} to {end_cell}")
        try:
            # H3 v4 API check: verify precise function name if needed
            return list(self.h3.grid_path_cells(start_cell, end_cell))
        except Exception as e:
            raise ValueError(f"Failed to calculate path: {e}") from e

    @_require_h3("get_cell_ring")
    def get_cell_ring(self, cell: str, k: int) -> List[str]:
        """
        Get the ring of cells at distance k.
        
        Args:
            cell: Center cell identifier
            k: Distance in grid steps
            
        Returns:
            List of cell identifiers in the ring
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cell or k matches invalid
        """
        logger.debug(f"Getting ring k={k} for {cell}")
        try:
            return list(self.h3.grid_ring(cell, k))
        except Exception as e:
            raise ValueError(f"Failed to get ring: {e}") from e

    # SpatialAnalyticsBackend implementation
    @_require_h3("analyze_hotspots")
    def analyze_hotspots(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze spatial hotspots in H3-indexed data.
        
        Args:
            data: Dictionary with 'cells' (list of H3 cell IDs) and 
                  'values' (corresponding numeric values).
                  Optional 'threshold' key for custom threshold.
                  
        Returns:
            Dictionary with:
                - hotspots: List of hotspot dictionaries
                - threshold: Threshold value used
                - total_cells: Number of input cells
                - hotspot_count: Number of identified hotspots
                
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cells and values have different lengths
        """
        cells = data.get('cells', [])
        values = data.get('values', [])

        if len(cells) != len(values):
            raise ValueError(f"Cells ({len(cells)}) and values ({len(values)}) must have the same length")

        logger.info(f"Analyzing hotspots for {len(cells)} cells")

        # Simple hotspot detection based on value thresholds
        hotspots = []
        threshold = data.get('threshold', 'median')

        if threshold == 'median':
            threshold_value = sorted(values)[len(values) // 2] if values else 0
        else:
            threshold_value = threshold

        for cell, value in zip(cells, values):
            if value > threshold_value:
                hotspots.append({
                    'cell': cell,
                    'value': value,
                    'intensity': 'high' if value > threshold_value * 1.5 else 'medium'
                })

        logger.info(f"Found {len(hotspots)} hotspots (threshold: {threshold_value})")
        
        return {
            'hotspots': hotspots,
            'threshold': threshold_value,
            'total_cells': len(cells),
            'hotspot_count': len(hotspots)
        }

    @_require_h3("compute_proximity")
    def compute_proximity(self, points: List[tuple[float, float]]) -> Dict[str, Any]:
        """
        Compute proximity analysis between points using H3.
        
        Args:
            points: List of (latitude, longitude) coordinate tuples
            
        Returns:
            Dictionary with:
                - proximity_pairs: List of pairwise distance information
                - total_points: Number of input points
                - analyzed_pairs: Number of successfully analyzed pairs
                
        Raises:
            H3UnavailableError: If H3 library is not installed
        """
        logger.info(f"Computing proximity for {len(points)} points")
        
        # Convert points to H3 cells and compute proximity
        cells = []
        for lat, lng in points:
            cell = self.h3.latlng_to_cell(lat, lng, 9)  # Use resolution 9
            cells.append(cell)

        # Calculate distances between cells
        distances = []
        for i, cell1 in enumerate(cells):
            for j, cell2 in enumerate(cells[i+1:], i+1):
                try:
                    distance = self.h3.grid_distance(cell1, cell2)
                    distances.append({
                        'from_cell': cell1,
                        'to_cell': cell2,
                        'distance': distance,
                        'from_point': points[i],
                        'to_point': points[j]
                    })
                except Exception as e:
                    logger.debug(f"Could not compute distance between {cell1} and {cell2}: {e}")
                    continue

        logger.info(f"Analyzed {len(distances)} proximity pairs")
        
        return {
            'proximity_pairs': distances,
            'total_points': len(points),
            'analyzed_pairs': len(distances)
        }

    @_require_h3("get_cell_resolution")
    def get_cell_resolution(self, cell: str) -> int:
        """
        Get the resolution level of an H3 cell.
        
        Args:
            cell: H3 cell identifier
            
        Returns:
            Resolution level (0-15)
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cell identifier is invalid
        """
        logger.debug(f"Getting resolution for cell: {cell}")
        
        try:
            resolution = self.h3.get_resolution(cell)
            logger.debug(f"Cell {cell} has resolution {resolution}")
            return resolution
        except Exception as e:
            raise ValueError(f"Invalid H3 cell identifier: {cell}") from e

    @_require_h3("get_cell_boundary")
    def get_cell_boundary(self, cell: str) -> List[Tuple[float, float]]:
        """
        Get the boundary coordinates of an H3 cell.
        
        Args:
            cell: H3 cell identifier
            
        Returns:
            List of (latitude, longitude) tuples forming the cell boundary
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cell identifier is invalid
        """
        logger.debug(f"Getting boundary for cell: {cell}")
        
        try:
            # H3 v4 returns boundary as list of LatLngPair
            boundary = self.h3.cell_to_boundary(cell)
            # Convert to list of tuples
            result = [(lat, lng) for lat, lng in boundary]
            logger.debug(f"Cell {cell} has {len(result)} boundary vertices")
            return result
        except Exception as e:
            raise ValueError(f"Invalid H3 cell identifier: {cell}") from e

    @_require_h3("get_cell_area")
    def get_cell_area(self, cell: str, unit: str = 'km^2') -> float:
        """
        Get the area of an H3 cell in square kilometers.
        
        Args:
            cell: H3 cell identifier
            unit: Unit for area calculation (default 'km^2')
            
        Returns:
            Area in specified unit
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cell identifier is invalid
        """
        logger.debug(f"Getting area for cell: {cell} in {unit}")
        
        try:
            # H3 v4 cell_area returns area in km² by default
            area = self.h3.cell_area(cell, unit=unit)
            logger.debug(f"Cell {cell} has area {area:.6f} {unit}")
            return area
        except Exception as e:
            raise ValueError(f"Invalid H3 cell identifier: {cell}") from e

    @_require_h3("cells_to_multipolygon")
    def cells_to_multipolygon(self, cells: List[str]) -> Dict[str, Any]:
        """
        Convert a list of H3 cells to a GeoJSON MultiPolygon geometry.
        
        Args:
            cells: List of H3 cell identifiers
            
        Returns:
            GeoJSON-like dictionary with 'type' and 'coordinates'
            
        Raises:
            H3UnavailableError: If H3 library is not installed
            ValueError: If cell identifiers are invalid
        """
        logger.info(f"Converting {len(cells)} cells to MultiPolygon")
        
        if not cells:
            return {"type": "MultiPolygon", "coordinates": []}
        
        try:
            polygons = []
            for cell in cells:
                # Get boundary for each cell
                boundary = self.h3.cell_to_boundary(cell)
                # Convert to GeoJSON format [lng, lat] and close the ring
                ring = [[lng, lat] for lat, lng in boundary]
                ring.append(ring[0])  # Close the ring
                polygons.append([ring])
            
            logger.info(f"Created MultiPolygon with {len(polygons)} polygons")
            return {
                "type": "MultiPolygon",
                "coordinates": polygons
            }
        except Exception as e:
            raise ValueError(f"Invalid H3 cell identifiers: {e}") from e
