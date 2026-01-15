"""
Comprehensive test suite for Unified Spatial Architecture.

This module provides extensive testing of the SpatialIndexingInterface
and the H3Backend implementation using the unified dispatch system.
"""

import pytest
import math
from typing import List, Dict, Any, Tuple

from geo_infer_space.core import get_backend_dispatcher, SpatialIndexingInterface

# Real-world test locations
LOCATIONS = {
    'san_francisco': (37.7749, -122.4194),
    'new_york': (40.7128, -74.0060),
    'london': (51.5074, -0.1278),
    'tokyo': (35.6762, 139.6503),
    'sydney': (-33.8688, 151.2093)
}

class TestUnifiedSpatialOperations:
    """Test core spatial operations via the unified interface."""
    
    def setup_method(self):
        """Setup the spatial interface for testing."""
        self.dispatcher = get_backend_dispatcher()
        # Ensure H3 backend is registered and active
        if 'h3' not in self.dispatcher.backends:
            from geo_infer_space.backends.h3.h3_backend import H3Backend
            self.dispatcher.register_backend('h3', H3Backend())
        self.interface = SpatialIndexingInterface()

    def test_coordinate_to_cell_real_locations(self):
        """Test coordinate to cell conversion with real locations."""
        for location_name, (lat, lng) in LOCATIONS.items():
            for resolution in [7, 8, 9, 10]:
                cell = self.interface.latlng_to_cell(lat, lng, resolution)
                
                # Basic validation
                assert isinstance(cell, str)
                
                # Check resolution
                res = self.interface.get_cell_resolution(cell)
                assert res == resolution
                
                # Round trip
                result_lat, result_lng = self.interface.cell_to_latlng(cell)
                assert abs(result_lat - lat) < 0.05, f"Latitude mismatch for {location_name}"
                assert abs(result_lng - lng) < 0.05, f"Longitude mismatch for {location_name}"
    
    def test_grid_relationships(self):
        """Test neighbor and hierarchy relationships."""
        # San Francisco
        lat, lng = LOCATIONS['san_francisco']
        center = self.interface.latlng_to_cell(lat, lng, 9)
        
        # Test Neighbors (k=1)
        neighbors = self.interface.get_cell_neighbors(center, k=1)
        assert len(neighbors) > 0
        assert center not in neighbors  # Usually implementations exclude self for k=1 unless k_ring
        
        # Verify distance to neighbors
        for neighbor in neighbors:
            dist = self.interface.get_cell_distance(center, neighbor)
            assert dist == 1
            
        # Test Hierarchy
        parent = self.interface.get_cell_parent(center, 8)
        assert self.interface.get_cell_resolution(parent) == 8
        
        children = self.interface.get_cell_children(parent, 9)
        assert center in children
        
    def test_path_finding_unified(self):
        """Test path finding between cells."""
        lat, lng = LOCATIONS['san_francisco']
        start = self.interface.latlng_to_cell(lat, lng, 9)
        # A nearby point
        end = self.interface.latlng_to_cell(lat + 0.01, lng + 0.01, 9)
        
        path = self.interface.get_cell_path(start, end)
        
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == end
        
    def test_polygon_operations(self):
        """Test polygon to cell operations."""
        # Small square polygon in GeoJSON format (coordinates are [lng, lat])
        polygon = {
            "type": "Polygon",
            "coordinates": [[
                [-122.42, 37.77],
                [-122.42, 37.78],
                [-122.41, 37.78],
                [-122.41, 37.77],
                [-122.42, 37.77]
            ]]
        }
        
        cells = self.interface.polygon_to_cells(polygon, resolution=9)
        assert len(cells) > 0
        
        # Convert back to multipolygon boundary
        multipoly = self.interface.cells_to_multipolygon(cells)
        assert len(multipoly) > 0  # Should be list of coordinates
    
    def test_cell_metrics(self):
        """Test cell property methods."""
        lat, lng = LOCATIONS['san_francisco']
        cell = self.interface.latlng_to_cell(lat, lng, 9)
        
        area_km2 = self.interface.get_cell_area(cell, unit='km^2')
        assert area_km2 > 0
        
        boundary = self.interface.get_cell_boundary(cell)
        assert len(boundary) >= 3 # At least a triangle, usually hexagon (6)

    def test_compaction(self):
        """Test compaction operations."""
        lat, lng = LOCATIONS['san_francisco']
        center = self.interface.latlng_to_cell(lat, lng, 9)
        
        # Get a disk
        neighbors = self.interface.get_cell_neighbors(center, k=2)
        cells = list(neighbors) + [center]
        
        compacted = self.interface.compact_cells(cells)
        # Should potentially be fewer cells
        assert len(compacted) <= len(cells)
        
        uncompacted = self.interface.uncompact_cells(compacted, resolution=9)
        assert set(uncompacted) == set(cells)
        
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
