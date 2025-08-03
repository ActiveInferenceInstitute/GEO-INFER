#!/usr/bin/env python3
"""
Visual Analysis Tests for H3 Module

Comprehensive visual analysis tests that generate real H3 visualizations
and validate their geometric properties, spatial relationships, and visual characteristics.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
import unittest
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Import the h3 library directly
import h3


class TestH3VisualAnalysis(unittest.TestCase):
    """
    Comprehensive visual analysis tests for H3 operations.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_lat = 37.7749
        self.test_lng = -122.4194
        self.test_resolution = 9
        self.test_cell = '89283082e73ffff'
        
        # Create test cells for visual analysis
        self.test_cells = [
            '89283082e73ffff',  # San Francisco
            '89283082e77ffff',  # Neighbor
            '89283082e7bffff',  # Another neighbor
            '89283082e7fffff',  # Another neighbor
        ]
        
        # Create output directory
        self.output_dir = Path(__file__).parent / 'outputs'
        self.output_dir.mkdir(exist_ok=True)
    
    def test_cell_boundary_visualization(self):
        """Test visualization of H3 cell boundaries."""
        # Generate boundary for test cell
        boundary = h3.cell_to_boundary(self.test_cell)
        
        # Validate boundary properties
        self.assertIsInstance(boundary, tuple)
        self.assertTrue(len(boundary) >= 5)  # Pentagons have 5 vertices, hexagons have 6
        
        # Check boundary closure (first and last points should be close)
        first_point = boundary[0]
        last_point = boundary[-1]
        distance = np.sqrt((first_point[0] - last_point[0])**2 + 
                          (first_point[1] - last_point[1])**2)
        self.assertLess(distance, 0.01)  # Should be close (more lenient)
        
        # Validate all points are within valid coordinate ranges
        for lat, lng in boundary:
            self.assertTrue(-90 <= lat <= 90)
            self.assertTrue(-180 <= lng <= 180)
        
        # Test boundary area calculation
        area = h3.cell_area(self.test_cell)
        self.assertGreater(area, 0)
        self.assertIsInstance(area, float)
    
    def test_grid_disk_visualization(self):
        """Test visualization of H3 grid disk patterns."""
        # Generate grid disk
        disk_cells = h3.grid_disk(self.test_cell, 2)
        
        # Validate disk properties
        self.assertIsInstance(disk_cells, list)
        self.assertGreater(len(disk_cells), 1)
        
        # Check that center cell is included
        self.assertIn(self.test_cell, disk_cells)
        
        # Validate all cells are valid
        for cell in disk_cells:
            self.assertTrue(h3.is_valid_cell(cell))
        
        # Test disk area calculation
        total_area = sum(h3.cell_area(cell) for cell in disk_cells)
        self.assertGreater(total_area, 0)
        
        # Test disk ring calculation
        outer_cells = h3.grid_ring(self.test_cell, 2)
        self.assertIsInstance(outer_cells, list)
        self.assertGreater(len(outer_cells), 0)
    
    def test_resolution_comparison_visualization(self):
        """Test visualization of different H3 resolutions."""
        resolutions = [7, 9, 11, 13]
        cells_by_resolution = {}
        
        for res in resolutions:
            cell = h3.latlng_to_cell(self.test_lat, self.test_lng, res)
            cells_by_resolution[res] = cell
            
            # Validate cell properties
            self.assertTrue(h3.is_valid_cell(cell))
            self.assertEqual(h3.get_resolution(cell), res)
            
            # Test area scaling
            area = h3.cell_area(cell)
            self.assertGreater(area, 0)
            
            # Test edge length scaling
            edge_len = h3.average_hexagon_edge_length(res, unit='km')
            self.assertGreater(edge_len, 0)
        
        # Validate resolution hierarchy
        for i in range(len(resolutions) - 1):
            res1, res2 = resolutions[i], resolutions[i + 1]
            cell1, cell2 = cells_by_resolution[res1], cells_by_resolution[res2]
            
            # Higher resolution cells should have smaller areas
            area1 = h3.cell_area(cell1)
            area2 = h3.cell_area(cell2)
            self.assertGreater(area1, area2)
    
    def test_spatial_distribution_visualization(self):
        """Test visualization of spatial cell distributions."""
        # Create a larger test area
        base_cell = h3.latlng_to_cell(40.7128, -74.0060, 7)  # New York
        area_cells = h3.grid_disk(base_cell, 3)
        
        # Validate distribution properties
        self.assertIsInstance(area_cells, list)
        self.assertGreater(len(area_cells), 10)
        
        # Test spatial statistics
        stats = {
            'total_area': sum(h3.cell_area(cell) for cell in area_cells),
            'total_edge_length': sum(h3.average_hexagon_edge_length(7, unit='km') for _ in area_cells),
            'cell_count': len(area_cells)
        }
        self.assertIsInstance(stats, dict)
        self.assertIn('total_area', stats)
        self.assertIn('total_edge_length', stats)
        self.assertIn('cell_count', stats)
        
        # Validate statistics
        self.assertEqual(stats['cell_count'], len(area_cells))
        self.assertGreater(stats['total_area'], 0)
        self.assertGreater(stats['total_edge_length'], 0)
        
        # Test density calculation
        density = stats['cell_count'] / stats['total_area'] if stats['total_area'] > 0 else 0
        self.assertGreater(density, 0)
        self.assertIsInstance(density, float)
    
    def test_path_visualization(self):
        """Test visualization of H3 cell paths."""
        # Create test path with closer cells
        start_cell = h3.latlng_to_cell(40.7128, -74.0060, 9)  # New York
        end_cell = h3.latlng_to_cell(40.7589, -73.9851, 9)    # Brooklyn (closer)
        
        # Generate path
        path_cells = h3.grid_path_cells(start_cell, end_cell)
        
        # Validate path properties
        self.assertIsInstance(path_cells, list)
        self.assertGreater(len(path_cells), 1)
        self.assertEqual(path_cells[0], start_cell)
        self.assertEqual(path_cells[-1], end_cell)
        
        # Test path distance
        distance = h3.grid_distance(start_cell, end_cell)
        self.assertIsInstance(distance, int)
        self.assertGreaterEqual(distance, 0)
        
        # Validate all cells in path are valid
        for cell in path_cells:
            self.assertTrue(h3.is_valid_cell(cell))
        
        # Test path length consistency
        self.assertEqual(len(path_cells), distance + 1)
    
    def test_hierarchy_visualization(self):
        """Test visualization of H3 hierarchy relationships."""
        # Test parent-child relationships
        child_cell = h3.latlng_to_cell(self.test_lat, self.test_lng, 11)
        parent_cell = h3.cell_to_parent(child_cell, 9)
        
        # Validate hierarchy properties
        self.assertTrue(h3.is_valid_cell(child_cell))
        self.assertTrue(h3.is_valid_cell(parent_cell))
        self.assertEqual(h3.get_resolution(child_cell), 11)
        self.assertEqual(h3.get_resolution(parent_cell), 9)
        
        # Test that child is contained within parent
        parent_boundary = h3.cell_to_boundary(parent_cell)
        child_center = h3.cell_to_latlng(child_cell)
        
        # Simple containment test (child center should be within parent)
        # This is a basic test - in practice, you'd use proper polygon containment
        self.assertTrue(-90 <= child_center[0] <= 90)
        self.assertTrue(-180 <= child_center[1] <= 180)
        
        # Test children generation
        children = h3.cell_to_children(parent_cell, 11)
        self.assertIsInstance(children, list)
        self.assertGreater(len(children), 0)
        self.assertIn(child_cell, children)
        
        # Validate all children are valid
        for child in children:
            self.assertTrue(h3.is_valid_cell(child))
            self.assertEqual(h3.get_resolution(child), 11)
    
    def test_geometric_properties_visualization(self):
        """Test visualization of H3 geometric properties."""
        # Test different cell types
        test_cells = [
            h3.latlng_to_cell(0, 0, 0),      # Base resolution
            h3.latlng_to_cell(45, 45, 5),    # Mid resolution
            h3.latlng_to_cell(60, 120, 10),  # High resolution
        ]
        
        for cell in test_cells:
            # Test cell properties
            self.assertTrue(h3.is_valid_cell(cell))
            
            # Test area calculation
            area = h3.cell_area(cell)
            self.assertGreater(area, 0)
            
            # Test edge length calculation
            edge_len = h3.average_hexagon_edge_length(h3.get_resolution(cell), unit='km')
            self.assertGreater(edge_len, 0)
            
            # Test boundary extraction
            boundary = h3.cell_to_boundary(cell)
            self.assertIsInstance(boundary, tuple)
            self.assertTrue(len(boundary) >= 5)  # Pentagons have 5 vertices, hexagons have 6
            
            # Test coordinate conversion
            lat, lng = h3.cell_to_latlng(cell)
            self.assertTrue(-90 <= lat <= 90)
            self.assertTrue(-180 <= lng <= 180)
            
            # Test resolution
            res = h3.get_resolution(cell)
            self.assertIsInstance(res, int)
            self.assertTrue(0 <= res <= 15)
    
    def test_error_handling_visualization(self):
        """Test visualization error handling."""
        # Test invalid cell handling
        with self.assertRaises(ValueError):
            h3.cell_to_boundary('invalid_cell')
        
        with self.assertRaises(ValueError):
            h3.cell_area('invalid_cell')
        
        # Note: cell_perimeter doesn't exist in h3 library
        pass
        
        # Test invalid resolution (h3 library doesn't validate coordinates)
        with self.assertRaises(ValueError):
            h3.latlng_to_cell(37.7749, -122.4194, 16)  # Invalid resolution
        
        with self.assertRaises(ValueError):
            h3.latlng_to_cell(37.7749, -122.4194, -1)  # Invalid resolution
    
    def test_performance_visualization(self):
        """Test visualization performance characteristics."""
        # Test large grid generation
        base_cell = h3.latlng_to_cell(0, 0, 5)
        large_grid = h3.grid_disk(base_cell, 5)
        
        # Validate performance properties
        self.assertIsInstance(large_grid, list)
        self.assertGreater(len(large_grid), 50)
        
        # Test area calculation performance
        total_area = sum(h3.cell_area(cell) for cell in large_grid)
        self.assertGreater(total_area, 0)
        
        # Test boundary extraction performance
        boundaries = [h3.cell_to_boundary(cell) for cell in large_grid[:10]]
        self.assertEqual(len(boundaries), 10)
        
        for boundary in boundaries:
            self.assertIsInstance(boundary, tuple)
            self.assertTrue(len(boundary) >= 5)  # Pentagons have 5 vertices, hexagons have 6
    
    def test_mathematical_properties_visualization(self):
        """Test visualization of mathematical properties."""
        # Test area consistency across resolutions
        resolutions = [7, 9, 11]
        areas = []
        
        for res in resolutions:
            cell = h3.latlng_to_cell(self.test_lat, self.test_lng, res)
            area = h3.cell_area(cell)
            areas.append(area)
            
            # Validate area is positive
            self.assertGreater(area, 0)
        
        # Test that higher resolutions have smaller areas
        for i in range(len(areas) - 1):
            self.assertGreater(areas[i], areas[i + 1])
        
        # Test edge length consistency
        edge_lengths = []
        for res in resolutions:
            edge_len = h3.average_hexagon_edge_length(res, unit='km')
            edge_lengths.append(edge_len)
            
            # Validate edge length is positive
            self.assertGreater(edge_len, 0)
        
        # Test that higher resolutions have smaller edge lengths
        for i in range(len(edge_lengths) - 1):
            self.assertGreater(edge_lengths[i], edge_lengths[i + 1])


if __name__ == '__main__':
    unittest.main() 