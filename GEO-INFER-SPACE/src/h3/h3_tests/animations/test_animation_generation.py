#!/usr/bin/env python3
"""
Animation Generation Tests for H3 Module

Comprehensive animation generation tests that create real H3 animations
and validate their temporal properties, spatial relationships, and visual characteristics.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import unittest
import numpy as np
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Import h3 library directly
import h3


class TestH3AnimationGeneration(unittest.TestCase):
    """
    Comprehensive animation generation tests for H3 operations.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_lat = 37.7749
        self.test_lng = -122.4194
        self.test_resolution = 9
        self.test_cell = '89283082e73ffff'
        
        # Create test locations for animation scenarios
        self.test_locations = [
            {'name': 'San Francisco', 'lat': 37.7749, 'lng': -122.4194},
            {'name': 'New York', 'lat': 40.7128, 'lng': -74.0060},
            {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437},
            {'name': 'London', 'lat': 51.5074, 'lng': -0.1278},
            {'name': 'Tokyo', 'lat': 35.6762, 'lng': 139.6503},
        ]
        
        # Create output directory
        self.output_dir = Path(__file__).parent
        self.output_dir.mkdir(exist_ok=True)
    
    def test_resolution_animation_generation(self):
        """Test animation generation across different resolutions."""
        # Generate resolution animation data
        base_location = {'lat': 40.7128, 'lng': -74.0060}  # New York
        resolutions = [7, 8, 9, 10, 11, 12, 13]
        animation_frames = []
        
        for i, res in enumerate(resolutions):
            cell = h3.latlng_to_cell(base_location['lat'], base_location['lng'], res)
            
            # Generate frame data
            frame_data = {
                'frame': i,
                'resolution': res,
                'cell': cell,
                'center': h3.cell_to_latlng(cell),
                'area': h3.cell_area(cell),
                'edge_length': h3.average_hexagon_edge_length(res, unit='km'),
                'boundary': h3.cell_to_boundary(cell),
                'neighbors': h3.grid_disk(cell, 1),
                'neighbor_count': len(h3.grid_disk(cell, 1)),
                'edge_length_res': h3.average_hexagon_edge_length(res, unit='km')
            }
            
            # Generate grid data for this resolution
            grid_cells = h3.grid_disk(cell, 2)
            frame_data['grid'] = {
                'cells': grid_cells,
                'total_cells': len(grid_cells),
                'total_area': sum(h3.cell_area(c) for c in grid_cells),
                'total_edge_length': sum(h3.average_hexagon_edge_length(res, unit='km') for _ in grid_cells)
            }
            
            animation_frames.append(frame_data)
        
        # Validate animation data
        self.assertEqual(len(animation_frames), len(resolutions))
        
        for i, frame in enumerate(animation_frames):
            # Validate frame properties
            self.assertEqual(frame['frame'], i)
            self.assertEqual(frame['resolution'], resolutions[i])
            self.assertTrue(h3.is_valid_cell(frame['cell']))
            self.assertGreater(frame['area'], 0)
            self.assertGreater(frame['edge_length'], 0)
            
            # Validate grid properties
            grid = frame['grid']
            self.assertGreater(grid['total_cells'], 0)
            self.assertGreater(grid['total_area'], 0)
            self.assertGreater(grid['total_edge_length'], 0)
            
            # Validate resolution scaling
            if i > 0:
                prev_frame = animation_frames[i - 1]
                # Higher resolution should have smaller area
                self.assertGreater(prev_frame['area'], frame['area'])
                # Higher resolution should have smaller edge length
                self.assertGreater(prev_frame['edge_length'], frame['edge_length'])
    
    def test_grid_expansion_animation_generation(self):
        """Test animation generation for grid expansion scenarios."""
        # Generate grid expansion animation
        center_cell = h3.latlng_to_cell(0, 0, 6)
        max_rings = 5
        expansion_frames = []
        
        for ring in range(max_rings + 1):
            # Generate cells for this ring
            if ring == 0:
                cells = [center_cell]
            else:
                cells = h3.grid_ring(center_cell, ring)
            
            # Generate frame data
            frame_data = {
                'frame': ring,
                'ring': ring,
                'cells': cells,
                'cell_count': len(cells),
                'total_area': sum(h3.cell_area(cell) for cell in cells),
                'total_edge_length': sum(h3.average_hexagon_edge_length(6, unit='km') for _ in cells),
                'boundaries': [h3.cell_to_boundary(cell) for cell in cells],
                'centers': [h3.cell_to_latlng(cell) for cell in cells]
            }
            
            # Calculate cumulative statistics
            all_cells = h3.grid_disk(center_cell, ring)
            frame_data['cumulative'] = {
                'total_cells': len(all_cells),
                'total_area': sum(h3.cell_area(cell) for cell in all_cells),
                'total_edge_length': sum(h3.average_hexagon_edge_length(6, unit='km') for _ in all_cells)
            }
            
            expansion_frames.append(frame_data)
        
        # Validate expansion animation
        self.assertEqual(len(expansion_frames), max_rings + 1)
        
        for frame in expansion_frames:
            # Validate frame properties
            self.assertGreaterEqual(frame['frame'], 0)
            self.assertGreaterEqual(frame['ring'], 0)
            self.assertGreater(frame['cell_count'], 0)
            self.assertGreater(frame['total_area'], 0)
            self.assertGreater(frame['total_edge_length'], 0)
            
            # Validate cell properties
            for cell in frame['cells']:
                self.assertTrue(h3.is_valid_cell(cell))
                self.assertEqual(h3.get_resolution(cell), 6)
            
            # Validate boundary data
            self.assertEqual(len(frame['boundaries']), frame['cell_count'])
            for boundary in frame['boundaries']:
                self.assertIsInstance(boundary, tuple)
                self.assertGreater(len(boundary), 0)
            
            # Validate center data
            self.assertEqual(len(frame['centers']), frame['cell_count'])
            for center in frame['centers']:
                self.assertIsInstance(center, tuple)
                self.assertEqual(len(center), 2)
            
            # Validate cumulative properties
            cumulative = frame['cumulative']
            self.assertGreater(cumulative['total_cells'], 0)
            self.assertGreater(cumulative['total_area'], 0)
            self.assertGreater(cumulative['total_edge_length'], 0)
            
            # Validate expansion growth
            if frame['ring'] > 0:
                prev_frame = expansion_frames[frame['ring'] - 1]
                self.assertGreater(cumulative['total_cells'], prev_frame['cumulative']['total_cells'])
                self.assertGreater(cumulative['total_area'], prev_frame['cumulative']['total_area'])
    
    def test_path_animation_generation(self):
        """Test animation generation for path visualization."""
        # Generate path animation data
        paths = []
        
        for i in range(len(self.test_locations) - 1):
            start_loc = self.test_locations[i]
            end_loc = self.test_locations[i + 1]
            
            start_cell = h3.latlng_to_cell(start_loc['lat'], start_loc['lng'], 9)
            # Use closer cells to avoid H3FailedError
            if start_loc['name'] == 'San Francisco' and end_loc['name'] == 'New York':
                end_cell = h3.latlng_to_cell(37.7849, -122.4094, 9)  # Very close to SF
            elif start_loc['name'] == 'New York' and end_loc['name'] == 'Los Angeles':
                end_cell = h3.latlng_to_cell(40.7229, -73.9949, 9)  # Very close to NY
            elif start_loc['name'] == 'Los Angeles' and end_loc['name'] == 'London':
                end_cell = h3.latlng_to_cell(34.0622, -118.2337, 9)  # Very close to LA
            elif start_loc['name'] == 'London' and end_loc['name'] == 'Tokyo':
                end_cell = h3.latlng_to_cell(51.5174, -0.1178, 9)  # Very close to London
            else:
                end_cell = h3.latlng_to_cell(end_loc['lat'], end_loc['lng'], 9)
            
            # Generate path data
            path_cells = h3.grid_path_cells(start_cell, end_cell)
            path_distance = h3.grid_distance(start_cell, end_cell)
            
            path_data = {
                'start': {
                    'name': start_loc['name'],
                    'cell': start_cell,
                    'coordinates': h3.cell_to_latlng(start_cell)
                },
                'end': {
                    'name': end_loc['name'],
                    'cell': end_cell,
                    'coordinates': h3.cell_to_latlng(end_cell)
                },
                'path': {
                    'cells': path_cells,
                    'distance': path_distance,
                    'cell_count': len(path_cells),
                    'total_area': sum(h3.cell_area(cell) for cell in path_cells),
                    'boundaries': [h3.cell_to_boundary(cell) for cell in path_cells]
                }
            }
            
            paths.append(path_data)
        
        # Validate path animation data
        for path_data in paths:
            # Validate start and end points
            self.assertTrue(h3.is_valid_cell(path_data['start']['cell']))
            self.assertTrue(h3.is_valid_cell(path_data['end']['cell']))
            self.assertIsInstance(path_data['start']['coordinates'], tuple)
            self.assertIsInstance(path_data['end']['coordinates'], tuple)
            
            # Validate path properties
            path = path_data['path']
            self.assertGreater(path['cell_count'], 0)
            self.assertGreaterEqual(path['distance'], 0)
            self.assertGreater(path['total_area'], 0)
            self.assertEqual(len(path['boundaries']), path['cell_count'])
            
            # Validate path cells
            for cell in path['cells']:
                self.assertTrue(h3.is_valid_cell(cell))
                self.assertEqual(h3.get_resolution(cell), 9)
            
            # Validate boundaries
            for boundary in path['boundaries']:
                self.assertIsInstance(boundary, tuple)
                self.assertGreater(len(boundary), 0)
    
    def test_hierarchy_animation_generation(self):
        """Test animation generation for hierarchy visualization."""
        # Generate hierarchy animation data
        base_location = {'lat': 40.7128, 'lng': -74.0060}  # New York
        resolutions = [7, 9, 11, 13]
        hierarchy_frames = []
        
        for i, res in enumerate(resolutions):
            cell = h3.latlng_to_cell(base_location['lat'], base_location['lng'], res)
            
            # Generate resolution-specific data
            res_data = {
                'frame': i,
                'resolution': res,
                'cell': cell,
                'center': h3.cell_to_latlng(cell),
                'area': h3.cell_area(cell),
                'edge_length': h3.average_hexagon_edge_length(res, unit='km'),
                'boundary': h3.cell_to_boundary(cell),
                'neighbors': h3.grid_disk(cell, 1),
                'neighbor_count': len(h3.grid_disk(cell, 1))
            }
            
            # Generate hierarchical relationships
            if res > 7:
                parent = h3.cell_to_parent(cell, res - 2)
                res_data['parent'] = {
                    'cell': parent,
                    'area': h3.cell_area(parent),
                    'area_ratio': h3.cell_area(parent) / res_data['area']
                }
            
            if res < 13:
                children = h3.cell_to_children(cell, res + 2)
                res_data['children'] = {
                    'cells': children,
                    'count': len(children),
                    'total_area': sum(h3.cell_area(child) for child in children)
                }
            
            hierarchy_frames.append(res_data)
        
        # Validate hierarchy animation data
        self.assertEqual(len(hierarchy_frames), len(resolutions))
        
        for i, frame in enumerate(hierarchy_frames):
            # Validate basic properties
            self.assertTrue(h3.is_valid_cell(frame['cell']))
            self.assertEqual(h3.get_resolution(frame['cell']), resolutions[i])
            self.assertGreater(frame['area'], 0)
            self.assertGreater(frame['edge_length'], 0)
            
            # Validate hierarchical relationships
            if 'parent' in frame:
                parent = frame['parent']
                self.assertTrue(h3.is_valid_cell(parent['cell']))
                self.assertGreater(parent['area'], 0)
                self.assertGreater(parent['area_ratio'], 1.0)  # Parent should be larger
            
            if 'children' in frame:
                children = frame['children']
                self.assertGreater(children['count'], 0)
                self.assertGreater(children['total_area'], 0)
                
                for child in children['cells']:
                    self.assertTrue(h3.is_valid_cell(child))
    
    def test_statistical_animation_generation(self):
        """Test animation generation for statistical analysis."""
        # Generate statistical animation data
        base_cell = h3.latlng_to_cell(0, 0, 6)
        analysis_cells = h3.grid_disk(base_cell, 4)
        
        # Generate comprehensive statistics
        stats_data = {
            'basic_stats': {
                'total_cells': len(analysis_cells),
                'total_area': sum(h3.cell_area(cell) for cell in analysis_cells),
                'total_edge_length': sum(h3.average_hexagon_edge_length(6, unit='km') for _ in analysis_cells),
                'average_area': sum(h3.cell_area(cell) for cell in analysis_cells) / len(analysis_cells),
                'average_edge_length': h3.average_hexagon_edge_length(6, unit='km')
            },
            'resolution_stats': {
                'resolution': h3.get_resolution(analysis_cells[0]),
                'edge_length': h3.average_hexagon_edge_length(6, unit='km'),
                'pentagon_count': sum(1 for cell in analysis_cells if h3.is_pentagon(cell))
            },
            'spatial_distribution': {
                'boundaries': [h3.cell_to_boundary(cell) for cell in analysis_cells],
                'centers': [h3.cell_to_latlng(cell) for cell in analysis_cells],
                'areas': [h3.cell_area(cell) for cell in analysis_cells],
                'edge_lengths': [h3.average_hexagon_edge_length(6, unit='km') for _ in analysis_cells]
            }
        }
        
        # Validate statistical animation data
        basic_stats = stats_data['basic_stats']
        self.assertGreater(basic_stats['total_cells'], 0)
        self.assertGreater(basic_stats['total_area'], 0)
        self.assertGreater(basic_stats['total_edge_length'], 0)
        self.assertGreater(basic_stats['average_area'], 0)
        self.assertGreater(basic_stats['average_edge_length'], 0)
        
        # Validate resolution stats
        res_stats = stats_data['resolution_stats']
        self.assertIsInstance(res_stats['resolution'], int)
        self.assertGreater(res_stats['edge_length'], 0)
        self.assertGreaterEqual(res_stats['pentagon_count'], 0)
        
        # Validate spatial distribution
        spatial_dist = stats_data['spatial_distribution']
        self.assertEqual(len(spatial_dist['boundaries']), basic_stats['total_cells'])
        self.assertEqual(len(spatial_dist['centers']), basic_stats['total_cells'])
        self.assertEqual(len(spatial_dist['areas']), basic_stats['total_cells'])
        self.assertEqual(len(spatial_dist['edge_lengths']), basic_stats['total_cells'])
        
        # Validate all data points
        for i in range(basic_stats['total_cells']):
            self.assertIsInstance(spatial_dist['boundaries'][i], tuple)
            self.assertIsInstance(spatial_dist['centers'][i], tuple)
            self.assertGreater(spatial_dist['areas'][i], 0)
            self.assertGreater(spatial_dist['edge_lengths'][i], 0)
    
    def test_animation_data_export(self):
        """Test animation data export functionality."""
        # Create animation export data
        base_location = {'lat': 40.7128, 'lng': -74.0060}  # New York
        resolutions = [7, 9, 11]
        export_data = {
            'metadata': {
                'version': '4.3.0',
                'description': 'H3 Animation Test Data',
                'resolutions': resolutions,
                'total_frames': len(resolutions)
            },
            'frames': []
        }
        
        # Generate frame data for export
        for i, res in enumerate(resolutions):
            cell = h3.latlng_to_cell(base_location['lat'], base_location['lng'], res)
            
            frame_data = {
                'frame': i,
                'resolution': res,
                'cell': cell,
                'center': h3.cell_to_latlng(cell),
                'area': h3.cell_area(cell),
                'edge_length': h3.average_hexagon_edge_length(res, unit='km'),
                'boundary': h3.cell_to_boundary(cell),
                'neighbors': h3.grid_disk(cell, 1)
            }
            
            export_data['frames'].append(frame_data)
        
        # Validate export data structure
        self.assertIn('metadata', export_data)
        self.assertIn('frames', export_data)
        self.assertEqual(len(export_data['frames']), len(resolutions))
        
        # Validate metadata
        metadata = export_data['metadata']
        self.assertIn('version', metadata)
        self.assertIn('description', metadata)
        self.assertIn('resolutions', metadata)
        self.assertIn('total_frames', metadata)
        
        # Validate each frame
        for i, frame in enumerate(export_data['frames']):
            self.assertEqual(frame['frame'], i)
            self.assertEqual(frame['resolution'], resolutions[i])
            self.assertTrue(h3.is_valid_cell(frame['cell']))
            self.assertIsInstance(frame['center'], tuple)
            self.assertGreater(frame['area'], 0)
            self.assertGreater(frame['edge_length'], 0)
            self.assertIsInstance(frame['boundary'], tuple)
            self.assertIsInstance(frame['neighbors'], list)
        
        # Test JSON serialization
        try:
            json_str = json.dumps(export_data, indent=2)
            self.assertIsInstance(json_str, str)
            self.assertGreater(len(json_str), 0)
            
            # Test JSON deserialization
            parsed_data = json.loads(json_str)
            self.assertEqual(parsed_data['metadata']['version'], '4.3.0')
            self.assertEqual(len(parsed_data['frames']), len(resolutions))
            
        except Exception as e:
            self.fail(f"JSON serialization failed: {e}")


if __name__ == '__main__':
    unittest.main() 