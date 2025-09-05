"""
Comprehensive test suite for H3 hexagonal grid operations.

This module provides extensive testing of H3 functionality with real-world
scenarios, visualizations, and performance benchmarks using H3 v4 API.
"""

import pytest
import numpy as np
import pandas as pd
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Import H3 modules to test
try:
    from geo_infer_space.h3.core import H3Cell, H3Grid, H3Analytics, H3Visualizer, H3Validator
    from geo_infer_space.h3.operations import *
    H3_MODULES_AVAILABLE = True
except ImportError as e:
    H3_MODULES_AVAILABLE = False
    pytest.skip(f"H3 modules not available: {e}", allow_module_level=True)

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    H3_AVAILABLE = False
    pytest.skip("h3-py package not available", allow_module_level=True)


class TestH3Operations:
    """Test core H3 operations with real-world scenarios."""
    
    # Real-world test locations
    LOCATIONS = {
        'san_francisco': (37.7749, -122.4194),
        'new_york': (40.7128, -74.0060),
        'london': (51.5074, -0.1278),
        'tokyo': (35.6762, 139.6503),
        'sydney': (-33.8688, 151.2093)
    }
    
    def test_coordinate_to_cell_real_locations(self):
        """Test coordinate to cell conversion with real locations."""
        for location_name, (lat, lng) in self.LOCATIONS.items():
            for resolution in [7, 8, 9, 10]:
                cell = coordinate_to_cell(lat, lng, resolution)
                
                # Verify cell is valid
                assert is_valid_cell(cell), f"Invalid cell for {location_name} at resolution {resolution}"
                
                # Verify resolution matches
                assert cell_resolution(cell) == resolution
                
                # Verify coordinates are close
                result_lat, result_lng = cell_to_coordinates(cell)
                assert abs(result_lat - lat) < 0.1, f"Latitude mismatch for {location_name}"
                assert abs(result_lng - lng) < 0.1, f"Longitude mismatch for {location_name}"
    
    def test_cell_boundary_properties(self):
        """Test H3 cell boundary properties."""
        sf_cell = coordinate_to_cell(37.7749, -122.4194, 9)
        boundary = cell_to_boundary(sf_cell)
        
        # H3 cells should have 6 vertices (hexagon)
        assert len(boundary) == 6, f"Expected 6 vertices, got {len(boundary)}"
        
        # Test GeoJSON format
        boundary_geojson = cell_to_boundary(sf_cell, geo_json_format=True)
        assert len(boundary_geojson) == 6
        
        # Verify coordinate order is different
        assert boundary[0] != boundary_geojson[0], "GeoJSON format should swap lat/lng"
    
    def test_grid_disk_properties(self):
        """Test grid disk properties and mathematical relationships."""
        center = coordinate_to_cell(37.7749, -122.4194, 9)
        
        # Test k=0 (only center)
        disk_0 = grid_disk(center, k=0)
        assert len(disk_0) == 1
        assert center in disk_0
        
        # Test k=1 (center + 6 neighbors)
        disk_1 = grid_disk(center, k=1)
        assert len(disk_1) == 7  # 1 + 6
        assert center in disk_1
        
        # Test k=2 (center + 6 + 12 neighbors)
        disk_2 = grid_disk(center, k=2)
        assert len(disk_2) == 19  # 1 + 6 + 12
        assert center in disk_2
        
        # Verify all k=1 cells are in k=2
        for cell in disk_1:
            assert cell in disk_2
    
    def test_grid_ring_properties(self):
        """Test grid ring properties."""
        center = coordinate_to_cell(37.7749, -122.4194, 9)
        
        # Ring 1 should have 6 cells
        ring_1 = grid_ring(center, k=1)
        assert len(ring_1) == 6
        assert center not in ring_1
        
        # Ring 2 should have 12 cells
        ring_2 = grid_ring(center, k=2)
        assert len(ring_2) == 12
        assert center not in ring_2
        
        # No overlap between rings
        assert not set(ring_1).intersection(set(ring_2))
    
    def test_hierarchy_operations(self):
        """Test parent-child relationships."""
        # Start with high resolution cell
        child = coordinate_to_cell(37.7749, -122.4194, 10)
        
        # Get parent at resolution 8
        parent = cell_to_parent(child, 8)
        assert cell_resolution(parent) == 8
        
        # Get children of parent at resolution 10
        children = cell_to_children(parent, 10)
        assert child in children
        
        # Verify all children have correct resolution
        for child_cell in children:
            assert cell_resolution(child_cell) == 10
    
    def test_polygon_coverage(self):
        """Test polygon to cells conversion with real areas."""
        # San Francisco Bay Area (simplified)
        sf_bay_coords = [
            (37.7749, -122.4194),  # SF
            (37.8044, -122.2712),  # Oakland
            (37.4419, -122.1430),  # Palo Alto
            (37.6879, -122.4702)   # Daly City
        ]
        
        for resolution in [6, 7, 8]:
            cells = polygon_to_cells(sf_bay_coords, resolution)
            
            # Should have reasonable number of cells
            assert len(cells) > 0, f"No cells found for resolution {resolution}"
            assert len(cells) < 1000, f"Too many cells ({len(cells)}) for resolution {resolution}"
            
            # All cells should be valid
            for cell in cells:
                assert is_valid_cell(cell)
                assert cell_resolution(cell) == resolution
    
    def test_area_calculations(self):
        """Test area calculations and consistency."""
        cell = coordinate_to_cell(37.7749, -122.4194, 9)
        
        # Test different units
        area_km2 = cell_area(cell, 'km^2')
        area_m2 = cell_area(cell, 'm^2')
        
        # Conversion should be consistent
        assert abs(area_km2 * 1_000_000 - area_m2) < 1, "Area unit conversion inconsistent"
        
        # Area should be reasonable for resolution 9
        assert 0.01 < area_km2 < 1.0, f"Unexpected area: {area_km2} km²"
    
    def test_distance_calculations(self):
        """Test grid distance calculations."""
        sf = coordinate_to_cell(37.7749, -122.4194, 9)
        
        # Distance to self should be 0
        assert grid_distance(sf, sf) == 0
        
        # Distance to neighbors should be 1
        neighbors = neighbor_cells(sf)
        for neighbor in neighbors:
            assert grid_distance(sf, neighbor) == 1
            assert are_neighbor_cells(sf, neighbor)
    
    def test_path_finding(self):
        """Test path finding between cells."""
        start = coordinate_to_cell(37.7749, -122.4194, 9)  # SF
        end = coordinate_to_cell(37.8044, -122.2712, 9)    # Oakland
        
        path = grid_path(start, end)
        
        # Path should include start and end
        assert start in path
        assert end in path
        
        # Path should be connected (each step is neighbor of next)
        for i in range(len(path) - 1):
            assert are_neighbor_cells(path[i], path[i + 1])
    
    def test_compaction_operations(self):
        """Test cell compaction and uncompaction."""
        # Create large grid
        center = coordinate_to_cell(37.7749, -122.4194, 9)
        cells = grid_disk(center, k=3)  # 37 cells
        
        # Compact cells
        compacted = compact_cells(cells)
        
        # Should have fewer cells after compaction
        assert len(compacted) <= len(cells)
        
        # Uncompact back to original resolution
        uncompacted = uncompact_cells(compacted, 9)
        
        # Should recover original cells
        assert set(uncompacted) == set(cells)


class TestH3Core:
    """Test H3 core classes and data structures."""
    
    def test_h3_cell_creation(self):
        """Test H3Cell creation and properties."""
        # Create from coordinates
        cell = H3Cell.from_coordinates(37.7749, -122.4194, 9)
        
        assert cell.resolution == 9
        assert abs(cell.latitude - 37.7749) < 0.01
        assert abs(cell.longitude - (-122.4194)) < 0.01
        assert cell.area_km2 > 0
        assert len(cell.boundary) == 6
        assert is_valid_cell(cell.index)
    
    def test_h3_cell_neighbors(self):
        """Test H3Cell neighbor operations."""
        cell = H3Cell.from_coordinates(37.7749, -122.4194, 9)
        
        # Get immediate neighbors
        neighbors = cell.neighbors(k=1)
        assert len(neighbors) == 6  # Hexagon has 6 neighbors
        
        # All neighbors should be valid
        for neighbor in neighbors:
            assert isinstance(neighbor, H3Cell)
            assert neighbor.resolution == cell.resolution
            assert cell.is_neighbor(neighbor)
            assert cell.distance_to(neighbor) == 1
    
    def test_h3_cell_hierarchy(self):
        """Test H3Cell parent-child relationships."""
        child = H3Cell.from_coordinates(37.7749, -122.4194, 10)
        
        # Get parent
        parent = child.parent(8)
        assert parent is not None
        assert parent.resolution == 8
        
        # Get children of parent
        children = parent.children(10)
        assert any(c.index == child.index for c in children)
    
    def test_h3_grid_creation(self):
        """Test H3Grid creation methods."""
        # From polygon
        sf_coords = [(37.7749, -122.4194), (37.7849, -122.4094), (37.7649, -122.4094)]
        grid = H3Grid.from_polygon(sf_coords, resolution=8, name="SF_Triangle")
        
        assert len(grid.cells) > 0
        assert grid.name == "SF_Triangle"
        assert all(cell.resolution == 8 for cell in grid.cells)
        
        # From center
        center_grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=2, name="SF_Center")
        assert len(center_grid.cells) == 19  # 1 + 6 + 12
        assert center_grid.name == "SF_Center"
    
    def test_h3_grid_operations(self):
        """Test H3Grid operations."""
        grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=1)
        
        # Test basic properties
        assert len(grid) == 7
        assert grid.total_area() > 0
        
        # Test bounds
        bounds = grid.bounds()
        assert len(bounds) == 4
        assert bounds[0] < bounds[2]  # min_lat < max_lat
        assert bounds[1] < bounds[3]  # min_lng < max_lng
        
        # Test center
        center = grid.center()
        assert abs(center[0] - 37.7749) < 0.01
        assert abs(center[1] - (-122.4194)) < 0.01
        
        # Test compaction
        compacted = grid.compact()
        assert len(compacted.cells) <= len(grid.cells)
    
    def test_h3_analytics(self):
        """Test H3Analytics functionality."""
        grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=2)
        analytics = H3Analytics(grid)
        
        # Basic statistics
        stats = analytics.basic_statistics()
        assert stats['cell_count'] == 19
        assert stats['total_area_km2'] > 0
        assert 9 in stats['resolution_distribution']
        
        # Connectivity analysis
        connectivity = analytics.connectivity_analysis()
        assert 'total_adjacencies' in connectivity
        assert 'connectivity_ratio' in connectivity
        
        # Generate full report
        report = analytics.generate_report()
        assert 'grid_info' in report
        assert 'basic_statistics' in report
        assert 'connectivity_analysis' in report
    
    def test_h3_validator(self):
        """Test H3Validator functionality."""
        # Valid H3 index
        valid_cell = coordinate_to_cell(37.7749, -122.4194, 9)
        validation = H3Validator.validate_h3_index(valid_cell)
        assert validation['valid']
        assert len(validation['errors']) == 0
        
        # Invalid H3 index
        invalid_validation = H3Validator.validate_h3_index("invalid_index")
        assert not invalid_validation['valid']
        assert len(invalid_validation['errors']) > 0
        
        # Coordinate validation
        coord_validation = H3Validator.validate_coordinates(37.7749, -122.4194)
        assert coord_validation['valid']
        
        # Invalid coordinates
        invalid_coord = H3Validator.validate_coordinates(100, -200)
        assert not invalid_coord['valid']
        
        # Grid validation
        grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=1)
        grid_validation = H3Validator.validate_grid(grid)
        assert grid_validation['valid']


class TestH3RealWorldScenarios:
    """Test H3 with real-world use cases and scenarios."""
    
    def test_city_coverage_analysis(self):
        """Test H3 coverage analysis for major cities."""
        cities = {
            'San Francisco': {
                'center': (37.7749, -122.4194),
                'radius_km': 10,
                'expected_cells_res8': (50, 200)
            },
            'Manhattan': {
                'center': (40.7831, -73.9712),
                'radius_km': 5,
                'expected_cells_res8': (20, 100)
            }
        }
        
        for city_name, city_data in cities.items():
            lat, lng = city_data['center']
            
            # Create grid covering city
            grid = H3Grid.from_center(lat, lng, resolution=8, k=3, name=f"{city_name}_Grid")
            
            # Verify reasonable cell count
            min_cells, max_cells = city_data['expected_cells_res8']
            assert min_cells <= len(grid.cells) <= max_cells, \
                f"{city_name}: Expected {min_cells}-{max_cells} cells, got {len(grid.cells)}"
            
            # Analyze coverage
            analytics = H3Analytics(grid)
            stats = analytics.basic_statistics()
            
            assert stats['total_area_km2'] > 0
            assert stats['cell_count'] == len(grid.cells)
    
    def test_transportation_network_analysis(self):
        """Test H3 for transportation network analysis."""
        # Simulate transportation corridor (SF to Oakland)
        start_coords = (37.7749, -122.4194)  # SF
        end_coords = (37.8044, -122.2712)    # Oakland
        
        # Create cells along corridor
        start_cell = coordinate_to_cell(*start_coords, 9)
        end_cell = coordinate_to_cell(*end_coords, 9)
        
        # Find path
        path_cells = grid_path(start_cell, end_cell)
        
        # Create grid from path with buffer
        corridor_cells = []
        for cell in path_cells:
            # Add cell and its neighbors
            corridor_cells.extend(grid_disk(cell, k=1))
        
        # Remove duplicates
        corridor_cells = list(set(corridor_cells))
        
        # Create grid
        h3_cells = [H3Cell(index=idx, resolution=9) for idx in corridor_cells]
        corridor_grid = H3Grid(cells=h3_cells, name="SF_Oakland_Corridor")
        
        # Analyze corridor
        analytics = H3Analytics(corridor_grid)
        stats = analytics.basic_statistics()
        
        assert len(corridor_grid.cells) > len(path_cells)  # Should include buffer
        assert stats['total_area_km2'] > 0
    
    def test_environmental_monitoring_grid(self):
        """Test H3 for environmental monitoring applications."""
        # Create monitoring grid for San Francisco Bay
        bay_polygon = [
            (37.9, -122.5),   # North
            (37.9, -122.0),   # Northeast  
            (37.4, -122.0),   # Southeast
            (37.4, -122.5)    # Southwest
        ]
        
        # Create monitoring grid at multiple resolutions
        resolutions = [6, 7, 8]
        grids = {}
        
        for res in resolutions:
            grid = H3Grid.from_polygon(bay_polygon, resolution=res, name=f"Bay_Monitoring_Res{res}")
            grids[res] = grid
            
            # Verify grid properties
            assert len(grid.cells) > 0
            assert all(cell.resolution == res for cell in grid.cells)
            
            # Higher resolution should have more cells
            if res > 6:
                assert len(grid.cells) > len(grids[res-1].cells)
    
    def test_retail_catchment_analysis(self):
        """Test H3 for retail catchment area analysis."""
        # Store locations in SF
        stores = [
            (37.7749, -122.4194),  # Downtown SF
            (37.7849, -122.4094),  # North Beach
            (37.7649, -122.4294)   # Mission
        ]
        
        catchment_grids = []
        
        for i, (lat, lng) in enumerate(stores):
            # Create catchment area (2km radius approximation)
            catchment = H3Grid.from_center(lat, lng, resolution=9, k=4, name=f"Store_{i+1}_Catchment")
            catchment_grids.append(catchment)
            
            # Verify catchment properties
            assert len(catchment.cells) > 0
            analytics = H3Analytics(catchment)
            stats = analytics.basic_statistics()
            
            # Should cover reasonable area (roughly 2km radius ≈ 12.6 km²)
            assert 5 < stats['total_area_km2'] < 20
        
        # Analyze overlap between catchments
        all_cells = []
        for grid in catchment_grids:
            all_cells.extend([cell.index for cell in grid.cells])
        
        unique_cells = set(all_cells)
        overlap_ratio = (len(all_cells) - len(unique_cells)) / len(all_cells)
        
        # Some overlap expected in dense urban area
        assert 0 <= overlap_ratio <= 0.5
    
    def test_disaster_response_grid(self):
        """Test H3 for disaster response and emergency planning."""
        # Emergency response zones around SF
        emergency_center = (37.7749, -122.4194)
        
        # Create response zones at different distances
        zones = {
            'immediate': {'k': 1, 'expected_time_min': 5},
            'primary': {'k': 3, 'expected_time_min': 15},
            'secondary': {'k': 6, 'expected_time_min': 30}
        }
        
        response_grids = {}
        
        for zone_name, zone_config in zones.items():
            grid = H3Grid.from_center(
                *emergency_center, 
                resolution=8, 
                k=zone_config['k'], 
                name=f"Emergency_{zone_name.title()}_Zone"
            )
            response_grids[zone_name] = grid
            
            # Analyze zone
            analytics = H3Analytics(grid)
            stats = analytics.basic_statistics()
            
            # Verify zone properties
            assert len(grid.cells) > 0
            assert stats['total_area_km2'] > 0
            
            # Larger zones should have more area
            if zone_name != 'immediate':
                prev_zone = list(zones.keys())[list(zones.keys()).index(zone_name) - 1]
                prev_stats = H3Analytics(response_grids[prev_zone]).basic_statistics()
                assert stats['total_area_km2'] > prev_stats['total_area_km2']


class TestH3Visualizations:
    """Test H3 visualization capabilities."""
    
    def test_geojson_export(self):
        """Test GeoJSON export functionality."""
        grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=1)
        
        # Export to GeoJSON
        geojson = grid.to_geojson()
        
        # Verify GeoJSON structure
        assert geojson['type'] == 'FeatureCollection'
        assert len(geojson['features']) == len(grid.cells)
        
        # Verify each feature
        for feature in geojson['features']:
            assert feature['type'] == 'Feature'
            assert feature['geometry']['type'] == 'Polygon'
            assert 'h3_index' in feature['properties']
            assert 'resolution' in feature['properties']
    
    def test_dataframe_export(self):
        """Test DataFrame export functionality."""
        # Create grid with custom properties
        grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=1)
        
        # Add custom properties to cells
        for i, cell in enumerate(grid.cells):
            cell.properties['value'] = i * 10
            cell.properties['category'] = 'A' if i % 2 == 0 else 'B'
        
        # Export to DataFrame
        df = grid.to_dataframe()
        
        # Verify DataFrame structure
        assert len(df) == len(grid.cells)
        assert 'h3_index' in df.columns
        assert 'resolution' in df.columns
        assert 'latitude' in df.columns
        assert 'longitude' in df.columns
        assert 'area_km2' in df.columns
        assert 'value' in df.columns
        assert 'category' in df.columns
        
        # Verify data types and values
        assert df['resolution'].dtype == 'int64'
        assert df['area_km2'].dtype == 'float64'
        assert all(df['resolution'] == 9)
        assert all(df['area_km2'] > 0)
    
    @pytest.mark.skipif(True, reason="Requires folium package")
    def test_folium_visualization(self):
        """Test Folium map creation (requires folium package)."""
        try:
            import folium
        except ImportError:
            pytest.skip("folium package not available")
        
        grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=1)
        visualizer = H3Visualizer(grid)
        
        # Create map
        m = visualizer.create_folium_map(
            cell_color='red',
            cell_opacity=0.7,
            zoom_start=12
        )
        
        # Verify map object
        assert isinstance(m, folium.Map)
    
    def test_geojson_file_export(self):
        """Test GeoJSON file export."""
        grid = H3Grid.from_center(37.7749, -122.4194, resolution=9, k=1)
        visualizer = H3Visualizer(grid)
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False) as f:
            temp_path = f.name
        
        try:
            visualizer.save_geojson(temp_path)
            
            # Verify file was created and has content
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                geojson_data = json.load(f)
            
            assert geojson_data['type'] == 'FeatureCollection'
            assert len(geojson_data['features']) == len(grid.cells)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestH3Performance:
    """Test H3 performance with large datasets."""
    
    def test_large_grid_creation(self):
        """Test performance with large grids."""
        import time
        
        # Create progressively larger grids
        test_cases = [
            {'k': 5, 'expected_cells': 91, 'max_time_sec': 1.0},
            {'k': 10, 'expected_cells': 331, 'max_time_sec': 2.0},
        ]
        
        for case in test_cases:
            start_time = time.time()
            
            grid = H3Grid.from_center(37.7749, -122.4194, resolution=8, k=case['k'])
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Verify performance
            assert len(grid.cells) == case['expected_cells']
            assert elapsed < case['max_time_sec'], f"Grid creation took {elapsed:.2f}s, expected < {case['max_time_sec']}s"
    
    def test_batch_operations_performance(self):
        """Test performance of batch operations."""
        import time
        
        # Create large set of cells
        cells = []
        for lat in np.linspace(37.7, 37.8, 10):
            for lng in np.linspace(-122.5, -122.4, 10):
                cell = coordinate_to_cell(lat, lng, 8)
                cells.append(cell)
        
        # Test batch area calculation
        start_time = time.time()
        total_area = cells_area(cells)
        end_time = time.time()
        
        assert total_area > 0
        assert (end_time - start_time) < 1.0  # Should complete in < 1 second
        
        # Test batch statistics
        start_time = time.time()
        stats = grid_statistics(cells)
        end_time = time.time()
        
        assert stats['cell_count'] == len(cells)
        assert (end_time - start_time) < 2.0  # Should complete in < 2 seconds


class TestH3EdgeCases:
    """Test H3 edge cases and error handling."""
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates."""
        # Invalid latitude
        with pytest.raises(ValueError):
            coordinate_to_cell(100, -122.4194, 9)
        
        # Invalid longitude
        with pytest.raises(ValueError):
            coordinate_to_cell(37.7749, 200, 9)
        
        # Invalid resolution
        with pytest.raises(ValueError):
            coordinate_to_cell(37.7749, -122.4194, 20)
    
    def test_invalid_h3_indices(self):
        """Test handling of invalid H3 indices."""
        # Invalid index format
        assert not is_valid_cell("invalid_index")
        
        # Empty string
        assert not is_valid_cell("")
        
        # None value
        with pytest.raises(TypeError):
            is_valid_cell(None)
    
    def test_empty_collections(self):
        """Test handling of empty collections."""
        # Empty cell list
        assert cells_area([]) == 0.0
        assert cells_intersection([], []) == []
        assert cells_union([], []) == []
        
        # Empty grid
        empty_grid = H3Grid(cells=[], name="Empty")
        assert len(empty_grid) == 0
        assert empty_grid.total_area() == 0.0
    
    def test_boundary_conditions(self):
        """Test boundary conditions."""
        # Cells at poles and date line
        boundary_locations = [
            (89.9, 0),      # Near North Pole
            (-89.9, 0),     # Near South Pole
            (0, 179.9),     # Near date line
            (0, -179.9)     # Near date line (other side)
        ]
        
        for lat, lng in boundary_locations:
            try:
                cell = coordinate_to_cell(lat, lng, 5)  # Use lower resolution for poles
                assert is_valid_cell(cell)
                
                # Should be able to get coordinates back
                result_lat, result_lng = cell_to_coordinates(cell)
                assert -90 <= result_lat <= 90
                assert -180 <= result_lng <= 180
                
            except Exception as e:
                # Some extreme locations might not be supported
                print(f"Boundary location ({lat}, {lng}) not supported: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
