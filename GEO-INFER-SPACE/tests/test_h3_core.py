#!/usr/bin/env python3
"""
H3 Core Module Tests

Comprehensive unit tests for H3 core operations using H3 v4.3.0.
Tests fundamental geospatial operations and coordinate conversions.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import pytest
import numpy as np
from typing import List, Tuple
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from h3.core import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_boundary,
    cell_to_polygon,
    polygon_to_cells,
    polyfill,
    cell_area,
    cell_perimeter,
    edge_length,
    num_cells,
    get_resolution,
    is_valid_cell,
    is_pentagon,
    is_class_iii,
    is_res_class_iii
)


class TestCoreOperations:
    """Test core H3 operations."""
    
    def test_latlng_to_cell_valid(self):
        """Test valid latitude/longitude to cell conversion."""
        lat, lng = 37.7749, -122.4194
        resolution = 9
        cell = latlng_to_cell(lat, lng, resolution)
        
        assert isinstance(cell, str)
        assert len(cell) == 15
        assert cell.startswith('8')
    
    def test_latlng_to_cell_invalid_resolution(self):
        """Test invalid resolution handling."""
        with pytest.raises(ValueError, match="Resolution must be between 0 and 15"):
            latlng_to_cell(37.7749, -122.4194, 20)
        
        with pytest.raises(ValueError, match="Resolution must be between 0 and 15"):
            latlng_to_cell(37.7749, -122.4194, -1)
    
    def test_latlng_to_cell_invalid_coordinates(self):
        """Test invalid coordinate handling."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            latlng_to_cell(91.0, -122.4194, 9)
        
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            latlng_to_cell(37.7749, 181.0, 9)
    
    def test_cell_to_latlng_valid(self):
        """Test valid cell to latitude/longitude conversion."""
        cell = '89283082e73ffff'
        lat, lng = cell_to_latlng(cell)
        
        assert isinstance(lat, float)
        assert isinstance(lng, float)
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180
    
    def test_cell_to_latlng_invalid(self):
        """Test invalid cell handling."""
        with pytest.raises(ValueError, match="Invalid H3 cell index"):
            cell_to_latlng('invalid')
    
    def test_cell_to_boundary_valid(self):
        """Test valid cell boundary extraction."""
        cell = '89283082e73ffff'
        boundary = cell_to_boundary(cell)
        
        assert isinstance(boundary, list)
        assert len(boundary) >= 6  # Hexagon has 6 vertices
        assert all(isinstance(coord, tuple) for coord in boundary)
        assert all(len(coord) == 2 for coord in boundary)
    
    def test_cell_to_boundary_invalid(self):
        """Test invalid cell boundary extraction."""
        with pytest.raises(ValueError, match="Invalid H3 cell index"):
            cell_to_boundary('invalid')
    
    def test_cell_to_polygon_valid(self):
        """Test valid cell to polygon conversion."""
        cell = '89283082e73ffff'
        polygon = cell_to_polygon(cell)
        
        assert isinstance(polygon, dict)
        assert polygon['type'] == 'Polygon'
        assert 'coordinates' in polygon
        assert len(polygon['coordinates']) == 1
    
    def test_polygon_to_cells_valid(self):
        """Test valid polygon to cells conversion."""
        polygon = {
            'type': 'Polygon',
            'coordinates': [[
                [37.7749, -122.4194],
                [37.7749, -122.4184],
                [37.7739, -122.4184],
                [37.7739, -122.4194],
                [37.7749, -122.4194]
            ]]
        }
        resolution = 9
        cells = polygon_to_cells(polygon, resolution)
        
        assert isinstance(cells, list)
        assert all(isinstance(cell, str) for cell in cells)
        assert all(len(cell) == 15 for cell in cells)
    
    def test_polygon_to_cells_invalid_polygon(self):
        """Test invalid polygon handling."""
        with pytest.raises(ValueError, match="Input must be a GeoJSON Polygon"):
            polygon_to_cells({'type': 'Point'}, 9)
    
    def test_polyfill_alias(self):
        """Test polyfill alias function."""
        polygon = {
            'type': 'Polygon',
            'coordinates': [[
                [37.7749, -122.4194],
                [37.7749, -122.4184],
                [37.7739, -122.4184],
                [37.7739, -122.4194],
                [37.7749, -122.4194]
            ]]
        }
        resolution = 9
        cells = polyfill(polygon, resolution)
        
        assert isinstance(cells, list)
        assert len(cells) > 0
    
    def test_cell_area_valid(self):
        """Test valid cell area calculation."""
        cell = '89283082e73ffff'
        area = cell_area(cell, 'km^2')
        
        assert isinstance(area, float)
        assert area > 0
    
    def test_cell_area_invalid(self):
        """Test invalid cell area calculation."""
        with pytest.raises(ValueError, match="Invalid H3 cell index"):
            cell_area('invalid', 'km^2')
    
    def test_cell_perimeter_valid(self):
        """Test valid cell perimeter calculation."""
        cell = '89283082e73ffff'
        perimeter = cell_perimeter(cell, 'km')
        
        assert isinstance(perimeter, float)
        assert perimeter > 0
    
    def test_edge_length_valid(self):
        """Test valid edge length calculation."""
        resolution = 9
        length = edge_length(resolution, 'km')
        
        assert isinstance(length, float)
        assert length > 0
    
    def test_edge_length_invalid(self):
        """Test invalid edge length calculation."""
        with pytest.raises(ValueError, match="Resolution must be between 0 and 15"):
            edge_length(20, 'km')
    
    def test_num_cells_valid(self):
        """Test valid number of cells calculation."""
        resolution = 9
        count = num_cells(resolution)
        
        assert isinstance(count, int)
        assert count > 0
    
    def test_get_resolution_valid(self):
        """Test valid resolution extraction."""
        cell = '89283082e73ffff'
        resolution = get_resolution(cell)
        
        assert isinstance(resolution, int)
        assert 0 <= resolution <= 15
    
    def test_is_valid_cell_valid(self):
        """Test valid cell validation."""
        assert is_valid_cell('89283082e73ffff') == True
        assert is_valid_cell('invalid') == False
    
    def test_is_pentagon_valid(self):
        """Test pentagon detection."""
        # Regular hexagon
        assert is_pentagon('89283082e73ffff') == False
        
        # Test with a known pentagon (resolution 0 pentagon)
        pentagon_cells = ['8001fffffffffff', '8003fffffffffff']
        for cell in pentagon_cells:
            if is_valid_cell(cell):
                assert is_pentagon(cell) == True
    
    def test_is_class_iii_valid(self):
        """Test Class III detection."""
        cell = '89283082e73ffff'
        is_class_iii_result = is_class_iii(cell)
        
        assert isinstance(is_class_iii_result, bool)
    
    def test_is_res_class_iii_valid(self):
        """Test Class III resolution detection."""
        # Resolution 9 is Class III
        assert is_res_class_iii(9) == True
        
        # Resolution 8 is Class II
        assert is_res_class_iii(8) == False
    
    def test_coordinate_roundtrip(self):
        """Test coordinate roundtrip conversion."""
        original_lat, original_lng = 37.7749, -122.4194
        resolution = 9
        
        cell = latlng_to_cell(original_lat, original_lng, resolution)
        result_lat, result_lng = cell_to_latlng(cell)
        
        # Allow for small floating point differences
        assert abs(original_lat - result_lat) < 0.001
        assert abs(original_lng - result_lng) < 0.001
    
    def test_multiple_resolutions(self):
        """Test operations across multiple resolutions."""
        lat, lng = 37.7749, -122.4194
        
        for resolution in range(0, 16):
            cell = latlng_to_cell(lat, lng, resolution)
            assert is_valid_cell(cell)
            assert get_resolution(cell) == resolution
            
            area = cell_area(cell, 'km^2')
            assert area > 0
            
            perimeter = cell_perimeter(cell, 'km')
            assert perimeter > 0
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test poles
        north_pole_cell = latlng_to_cell(90.0, 0.0, 0)
        south_pole_cell = latlng_to_cell(-90.0, 0.0, 0)
        
        assert is_valid_cell(north_pole_cell)
        assert is_valid_cell(south_pole_cell)
        
        # Test international date line
        date_line_cell = latlng_to_cell(0.0, 180.0, 0)
        assert is_valid_cell(date_line_cell)
        
        # Test prime meridian
        prime_meridian_cell = latlng_to_cell(0.0, 0.0, 0)
        assert is_valid_cell(prime_meridian_cell)


class TestCorePerformance:
    """Test core operations performance."""
    
    def test_bulk_operations(self):
        """Test bulk operations performance."""
        import time
        
        # Generate test coordinates
        lats = np.random.uniform(-90, 90, 1000)
        lngs = np.random.uniform(-180, 180, 1000)
        resolution = 9
        
        start_time = time.time()
        cells = [latlng_to_cell(lat, lng, resolution) for lat, lng in zip(lats, lngs)]
        end_time = time.time()
        
        assert len(cells) == 1000
        assert all(is_valid_cell(cell) for cell in cells)
        assert end_time - start_time < 1.0  # Should complete in under 1 second
    
    def test_memory_efficiency(self):
        """Test memory efficiency of operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        cells = []
        for i in range(10000):
            lat = np.random.uniform(-90, 90)
            lng = np.random.uniform(-180, 180)
            cell = latlng_to_cell(lat, lng, 9)
            cells.append(cell)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__]) 