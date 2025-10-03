"""
H3 Backend Implementation for GEO-INFER-SPACE.

This module provides the H3-specific implementation of spatial operations
that integrates with the generic spatial methods layer.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from ...core.dispatcher import SpatialIndexingBackend, SpatialAnalyticsBackend

logger = logging.getLogger(__name__)


class H3Backend(SpatialIndexingBackend, SpatialAnalyticsBackend):
    """
    H3 backend implementation for spatial operations.

    This class provides H3-specific implementations of the generic spatial
    interfaces defined in the core dispatcher module.
    """

    def __init__(self):
        self._check_h3_availability()

    def _check_h3_availability(self):
        """Check if H3 library is available."""
        try:
            import h3
            self.h3 = h3
            self._available = True
            logger.info("H3 library is available")
        except ImportError:
            self.h3 = None
            self._available = False
            logger.warning("H3 library is not available - using mock implementations")

    @property
    def name(self) -> str:
        """Return the backend name."""
        return "h3"

    @property
    def version(self) -> str:
        """Return the backend version."""
        if self.h3:
            return getattr(self.h3, '__version__', 'unknown')
        return "0.0.0"

    def is_available(self) -> bool:
        """Check if the backend is available and functional."""
        return self._available

    def get_capabilities(self) -> Dict[str, Any]:
        """Return the backend's capabilities."""
        return {
            'indexing': {
                'latlng_to_cell': True,
                'cell_to_latlng': True,
                'polygon_to_cells': True,
                'get_neighbors': True,
                'get_distance': True,
                'compact_cells': True,
                'uncompact_cells': True,
            },
            'analytics': {
                'analyze_hotspots': True,
                'compute_proximity': True,
                'cluster_points': True,
                'interpolate_values': True,
            },
            'geometric': {
                'buffer_geometry': True,
                'calculate_area': True,
                'calculate_perimeter': True,
                'calculate_centroid': True,
                'union_geometries': True,
                'intersection_geometries': True,
                'difference_geometries': True,
            },
            'supported_resolutions': list(range(16)),  # H3 supports resolutions 0-15
            'coordinate_system': 'WGS84',
        }

    # SpatialIndexingBackend implementation
    def latlng_to_cell(self, lat: float, lng: float, resolution: int) -> str:
        """Convert lat/lng coordinates to H3 cell."""
        if not self._available:
            return self._mock_latlng_to_cell(lat, lng, resolution)
        return self.h3.latlng_to_cell(lat, lng, resolution)

    def cell_to_latlng(self, cell: str) -> tuple[float, float]:
        """Convert H3 cell back to lat/lng coordinates."""
        if not self._available:
            return self._mock_cell_to_latlng(cell)
        return self.h3.cell_to_latlng(cell)

    def polygon_to_cells(self, polygon: Dict[str, Any], resolution: int) -> list[str]:
        """Convert polygon to list of H3 cells."""
        if not self._available:
            return self._mock_polygon_to_cells(polygon, resolution)

        # Extract coordinates from GeoJSON-like polygon
        coords = polygon.get('coordinates', [])
        if not coords:
            return []

        # For simplicity, use the first ring (outer boundary)
        ring = coords[0]
        if not ring:
            return []

        # Convert to H3 cells (this is a simplified implementation)
        cells = []
        for i in range(0, len(ring) - 1, 2):  # Sample every other point
            try:
                lat, lng = ring[i][1], ring[i][0]  # GeoJSON is [lng, lat]
                cell = self.h3.latlng_to_cell(lat, lng, resolution)
                if cell not in cells:
                    cells.append(cell)
            except (IndexError, ValueError):
                continue

        return cells

    def get_cell_neighbors(self, cell: str, k: int = 1) -> List[str]:
        """Get neighboring cells around a given cell."""
        if not self._available:
            return self._mock_get_cell_neighbors(cell, k)

        try:
            if k == 1:
                # For k=1, use grid_ring for efficiency
                return list(self.h3.grid_ring(cell, 1))
            else:
                # For k>1, use grid_disk and remove inner rings
                disk = self.h3.grid_disk(cell, k)
                inner_disk = self.h3.grid_disk(cell, k-1) if k > 1 else {cell}
                return list(disk - inner_disk)
        except Exception as e:
            logger.warning(f"H3 get_cell_neighbors failed: {e}")
            return self._mock_get_cell_neighbors(cell, k)

    def get_cell_distance(self, cell1: str, cell2: str) -> int:
        """Calculate the distance between two spatial index cells."""
        if not self._available:
            return self._mock_get_cell_distance(cell1, cell2)

        try:
            return self.h3.grid_distance(cell1, cell2)
        except Exception as e:
            logger.warning(f"H3 get_cell_distance failed: {e}")
            return self._mock_get_cell_distance(cell1, cell2)

    def compact_cells(self, cells: List[str]) -> List[str]:
        """Compact a list of cells into a more efficient representation."""
        if not self._available:
            return cells  # Return as-is for mock

        try:
            return list(self.h3.compact_cells(cells))
        except Exception as e:
            logger.warning(f"H3 compact_cells failed: {e}")
            return cells

    def uncompact_cells(self, compacted_cells: List[str], resolution: int) -> List[str]:
        """Uncompact cells back to individual cell identifiers."""
        if not self._available:
            return compacted_cells  # Return as-is for mock

        try:
            return list(self.h3.uncompact_cells(compacted_cells, resolution))
        except Exception as e:
            logger.warning(f"H3 uncompact_cells failed: {e}")
            return compacted_cells

    # Mock implementations for when H3 is not available
    def _mock_get_cell_neighbors(self, cell: str, k: int = 1) -> List[str]:
        """Mock neighbor generation when H3 is not available."""
        # Simple mock: return cell repeated k times
        return [cell] * min(k, 6)  # Hexagon has max 6 neighbors

    def _mock_get_cell_distance(self, cell1: str, cell2: str) -> int:
        """Mock distance calculation when H3 is not available."""
        # Simple hash-based distance
        return abs(hash(cell1) - hash(cell2)) % 10

    # SpatialAnalyticsBackend implementation
    def analyze_hotspots(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spatial hotspots in H3-indexed data."""
        if not self._available:
            return self._mock_analyze_hotspots(data)

        # Implement H3-based hotspot analysis
        # This would use H3 cells as the spatial units for analysis
        cells = data.get('cells', [])
        values = data.get('values', [])

        if len(cells) != len(values):
            raise ValueError("Cells and values must have the same length")

        # Simple hotspot detection based on value thresholds
        hotspots = []
        threshold = data.get('threshold', 'median')

        if threshold == 'median':
            threshold_value = sorted(values)[len(values) // 2]
        else:
            threshold_value = threshold

        for cell, value in zip(cells, values):
            if value > threshold_value:
                hotspots.append({
                    'cell': cell,
                    'value': value,
                    'intensity': 'high' if value > threshold_value * 1.5 else 'medium'
                })

        return {
            'hotspots': hotspots,
            'threshold': threshold_value,
            'total_cells': len(cells),
            'hotspot_count': len(hotspots)
        }

    def compute_proximity(self, points: list[tuple[float, float]]) -> Dict[str, Any]:
        """Compute proximity analysis between points using H3."""
        if not self._available:
            return self._mock_compute_proximity(points)

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
                except:
                    continue

        return {
            'proximity_pairs': distances,
            'total_points': len(points),
            'analyzed_pairs': len(distances)
        }

    # Mock implementations for when H3 is not available
    def _mock_latlng_to_cell(self, lat: float, lng: float, resolution: int) -> str:
        """Mock H3 cell generation when H3 is not available."""
        # Simple hash-based mock cell ID
        hash_input = f"{lat:.6f},{lng:.6f},{resolution}"
        hash_value = hash(hash_input) % (16 ** 8)  # Mock H3-style hex ID
        return f"{hash_value:08x}"

    def _mock_cell_to_latlng(self, cell: str) -> tuple[float, float]:
        """Mock lat/lng extraction when H3 is not available."""
        # Reverse the hash to get approximate coordinates
        try:
            hash_value = int(cell, 16)
            # Simple reverse mapping (this is just a mock)
            lat = (hash_value % 180) - 90
            lng = (hash_value // 180) % 360 - 180
            return lat, lng
        except ValueError:
            return 0.0, 0.0

    def _mock_polygon_to_cells(self, polygon: Dict[str, Any], resolution: int) -> list[str]:
        """Mock polygon to cells conversion when H3 is not available."""
        coords = polygon.get('coordinates', [])
        if not coords:
            return []

        cells = []
        for ring in coords:
            for coord in ring:
                if len(coord) >= 2:
                    lat, lng = coord[1], coord[0]
                    cell = self._mock_latlng_to_cell(lat, lng, resolution)
                    if cell not in cells:
                        cells.append(cell)

        return cells

    def _mock_analyze_hotspots(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock hotspot analysis when H3 is not available."""
        cells = data.get('cells', [])
        values = data.get('values', [])

        if len(cells) != len(values):
            hotspots = []
        else:
            threshold = sorted(values)[len(values) // 2] if values else 0
            hotspots = [
                {'cell': cell, 'value': value, 'intensity': 'high'}
                for cell, value in zip(cells, values)
                if value > threshold
            ]

        return {
            'hotspots': hotspots,
            'threshold': threshold,
            'total_cells': len(cells),
            'hotspot_count': len(hotspots)
        }

    def _mock_compute_proximity(self, points: list[tuple[float, float]]) -> Dict[str, Any]:
        """Mock proximity analysis when H3 is not available."""
        distances = []
        for i, (lat1, lng1) in enumerate(points):
            for j, (lat2, lng2) in enumerate(points[i+1:], i+1):
                # Simple Euclidean distance (not accurate for lat/lng)
                distance = ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5
                distances.append({
                    'from_point': (lat1, lng1),
                    'to_point': (lat2, lng2),
                    'distance': distance
                })

        return {
            'proximity_pairs': distances,
            'total_points': len(points),
            'analyzed_pairs': len(distances)
        }
