"""
Tests for H3 operations module.

Comprehensive test suite covering all H3 operations including coordinate conversion,
grid operations, hierarchy operations, area calculations, and analysis functions.
"""

import pytest
import math
from typing import Set, List, Dict, Any

from geo_infer_space.h3.operations import (
    coordinate_to_cell, cell_to_coordinates, cell_to_boundary, cells_to_geojson,
    grid_disk, grid_ring, grid_distance, grid_path,
    cell_to_parent, cell_to_children, compact_cells, uncompact_cells,
    polygon_to_cells, cells_to_polygon, cell_area, cells_area,
    neighbor_cells, cell_resolution, is_valid_cell, are_neighbor_cells,
    cells_intersection, cells_union, cells_difference, grid_statistics,
    get_resolution_info, find_optimal_resolution, create_h3_grid_for_bounds
)

# Test data
SF_LAT, SF_LNG = 37.7749, -122.4194
VALID_H3_CELL = "89283082803ffff"
RESOLUTION = 9


class TestCoordinateOperations:
    """Test coordinate conversion operations."""
    
    def test_coordinate_to_cell(self):
        """Test coordinate to H3 cell conversion."""
        cell = coordinate_to_cell(SF_LAT, SF_LNG, RESOLUTION)
        assert isinstance(cell, str)
        assert len(cell) == 15
        assert is_valid_cell(cell)
    
    def test_coordinate_to_cell_validation(self):
        """Test coordinate validation."""
        with pytest.raises(ValueError, match="Latitude.*must be between -90 and 90"):
            coordinate_to_cell(91.0, SF_LNG, RESOLUTION)
        
        with pytest.raises(ValueError, match="Longitude.*must be between -180 and 180"):
            coordinate_to_cell(SF_LAT, 181.0, RESOLUTION)
        
        with pytest.raises(ValueError, match="Resolution.*must be between 0 and 15"):
            coordinate_to_cell(SF_LAT, SF_LNG, 16)
    
    def test_cell_to_coordinates(self):
        """Test H3 cell to coordinate conversion."""
        coords = cell_to_coordinates(VALID_H3_CELL)
        assert isinstance(coords, tuple)
        assert len(coords) == 2
        assert -90 <= coords[0] <= 90  # latitude
        assert -180 <= coords[1] <= 180  # longitude
    
    def test_coordinate_roundtrip(self):
        """Test coordinate to cell and back conversion."""
        cell = coordinate_to_cell(SF_LAT, SF_LNG, RESOLUTION)
        lat, lng = cell_to_coordinates(cell)
        
        # Should be close to original coordinates
        assert abs(lat - SF_LAT) < 0.01
        assert abs(lng - SF_LNG) < 0.01
    
    def test_cell_to_boundary(self):
        """Test getting cell boundary coordinates."""
        boundary = cell_to_boundary(VALID_H3_CELL)
        assert isinstance(boundary, list)
        assert len(boundary) == 6  # Hexagon has 6 vertices
        
        for coord in boundary:
            assert isinstance(coord, tuple)
            assert len(coord) == 2
            assert -90 <= coord[0] <= 90
            assert -180 <= coord[1] <= 180
    
    def test_cells_to_geojson(self):
        """Test converting cells to GeoJSON."""
        cells = [VALID_H3_CELL]
        geojson = cells_to_geojson(cells)
        
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == 1
        
        feature = geojson["features"][0]
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Polygon"
        assert "h3_index" in feature["properties"]
        assert "resolution" in feature["properties"]


class TestGridOperations:
    """Test grid traversal and distance operations."""
    
    def test_grid_disk(self):
        """Test k-ring (grid disk) operation."""
        # k=0 should return just the center cell
        disk_0 = grid_disk(VALID_H3_CELL, 0)
        assert len(disk_0) == 1
        assert VALID_H3_CELL in disk_0
        
        # k=1 should return center + 6 neighbors = 7 cells
        disk_1 = grid_disk(VALID_H3_CELL, 1)
        assert len(disk_1) == 7
        assert VALID_H3_CELL in disk_1
        
        # k=2 should return more cells
        disk_2 = grid_disk(VALID_H3_CELL, 2)
        assert len(disk_2) > len(disk_1)
        assert set(disk_1).issubset(set(disk_2))
    
    def test_grid_ring(self):
        """Test grid ring operation."""
        ring_1 = grid_ring(VALID_H3_CELL, 1)
        assert len(ring_1) == 6  # 6 immediate neighbors
        assert VALID_H3_CELL not in ring_1
        
        ring_2 = grid_ring(VALID_H3_CELL, 2)
        assert len(ring_2) == 12  # 12 cells at distance 2
        assert VALID_H3_CELL not in ring_2
        assert set(ring_1).isdisjoint(set(ring_2))
    
    def test_grid_distance(self):
        """Test grid distance calculation."""
        # Distance to self should be 0
        assert grid_distance(VALID_H3_CELL, VALID_H3_CELL) == 0
        
        # Get a neighbor and test distance
        neighbors = grid_ring(VALID_H3_CELL, 1)
        neighbor = next(iter(neighbors))
        assert grid_distance(VALID_H3_CELL, neighbor) == 1
    
    def test_grid_path(self):
        """Test grid path finding."""
        neighbors = grid_ring(VALID_H3_CELL, 1)
        neighbor = next(iter(neighbors))
        
        path = grid_path(VALID_H3_CELL, neighbor)
        assert isinstance(path, list)
        assert len(path) >= 2
        assert path[0] == VALID_H3_CELL
        assert path[-1] == neighbor
    
    def test_neighbor_cells(self):
        """Test getting immediate neighbors."""
        neighbors = neighbor_cells(VALID_H3_CELL)
        assert len(neighbors) == 6
        assert VALID_H3_CELL not in neighbors
        
        # All neighbors should be at distance 1
        for neighbor in neighbors:
            assert grid_distance(VALID_H3_CELL, neighbor) == 1
    
    def test_are_neighbor_cells(self):
        """Test neighbor relationship checking."""
        neighbors = neighbor_cells(VALID_H3_CELL)
        neighbor = next(iter(neighbors))
        
        assert are_neighbor_cells(VALID_H3_CELL, neighbor)
        assert not are_neighbor_cells(VALID_H3_CELL, VALID_H3_CELL)


class TestHierarchyOperations:
    """Test hierarchy and resolution operations."""
    
    def test_cell_resolution(self):
        """Test getting cell resolution."""
        resolution = cell_resolution(VALID_H3_CELL)
        assert isinstance(resolution, int)
        assert 0 <= resolution <= 15
    
    def test_cell_to_parent(self):
        """Test getting parent cell."""
        current_res = cell_resolution(VALID_H3_CELL)
        if current_res > 0:
            parent_res = current_res - 1
            parent = cell_to_parent(VALID_H3_CELL, parent_res)
            
            assert is_valid_cell(parent)
            assert cell_resolution(parent) == parent_res
    
    def test_cell_to_children(self):
        """Test getting children cells."""
        current_res = cell_resolution(VALID_H3_CELL)
        if current_res < 15:
            child_res = current_res + 1
            children = cell_to_children(VALID_H3_CELL, child_res)
            
            assert isinstance(children, list)
            assert len(children) == 7  # H3 aperture 7
            
            for child in children:
                assert is_valid_cell(child)
                assert cell_resolution(child) == child_res
    
    def test_compact_uncompact_cells(self):
        """Test cell compaction and uncompaction."""
        # Get a set of cells
        cells = grid_disk(VALID_H3_CELL, 1)
        
        # Compact them
        compacted = compact_cells(cells)
        assert isinstance(compacted, list)
        assert len(compacted) <= len(cells)
        
        # Uncompact back to original resolution
        original_res = cell_resolution(VALID_H3_CELL)
        uncompacted = uncompact_cells(compacted, original_res)
        assert isinstance(uncompacted, list)


class TestAreaOperations:
    """Test area and polygon operations."""
    
    def test_cell_area(self):
        """Test calculating cell area."""
        area_km2 = cell_area(VALID_H3_CELL, 'km^2')
        area_m2 = cell_area(VALID_H3_CELL, 'm^2')
        
        assert area_km2 > 0
        assert area_m2 > 0
        assert area_m2 == area_km2 * 1_000_000
    
    def test_cells_area(self):
        """Test calculating total area of multiple cells."""
        cells = grid_disk(VALID_H3_CELL, 1)
        total_area = cells_area(cells, 'km^2')
        
        assert total_area > 0
        
        # Should be approximately 7 times the area of one cell
        single_area = cell_area(VALID_H3_CELL, 'km^2')
        expected_area = single_area * len(cells)
        assert abs(total_area - expected_area) < expected_area * 0.1
    
    def test_polygon_to_cells(self):
        """Test converting polygon to H3 cells."""
        # Create a small square polygon
        polygon_coords = [
            (SF_LAT, SF_LNG),
            (SF_LAT + 0.01, SF_LNG),
            (SF_LAT + 0.01, SF_LNG + 0.01),
            (SF_LAT, SF_LNG + 0.01)
        ]
        
        cells = polygon_to_cells(polygon_coords, RESOLUTION)
        assert isinstance(cells, list)
        assert len(cells) > 0
        
        # All cells should be valid
        for cell in cells:
            assert is_valid_cell(cell)
    
    def test_cells_to_polygon(self):
        """Test converting cells to polygon boundary."""
        cells = grid_disk(VALID_H3_CELL, 1)
        boundary = cells_to_polygon(cells)
        
        assert isinstance(boundary, list)
        assert len(boundary) > 0
        
        # All coordinates should be valid
        for coord in boundary:
            assert isinstance(coord, tuple)
            assert len(coord) == 2
            assert -90 <= coord[0] <= 90
            assert -180 <= coord[1] <= 180


class TestSetOperations:
    """Test set operations on H3 cells."""
    
    def test_cells_intersection(self):
        """Test cell set intersection."""
        set1 = grid_disk(VALID_H3_CELL, 1)
        set2 = grid_disk(VALID_H3_CELL, 2)
        
        intersection = cells_intersection(set1, set2)
        assert set(intersection) == set(set1)  # set1 is subset of set2
    
    def test_cells_union(self):
        """Test cell set union."""
        set1 = grid_disk(VALID_H3_CELL, 1)
        neighbors = neighbor_cells(VALID_H3_CELL)
        neighbor = next(iter(neighbors))
        set2 = grid_disk(neighbor, 1)
        
        union = cells_union(set1, set2)
        assert len(union) >= len(set1)
        assert len(union) >= len(set2)
        assert set(set1).issubset(set(union))
        assert set(set2).issubset(set(union))
    
    def test_cells_difference(self):
        """Test cell set difference."""
        set1 = grid_disk(VALID_H3_CELL, 2)
        set2 = grid_disk(VALID_H3_CELL, 1)
        
        difference = cells_difference(set1, set2)
        assert len(difference) == len(set1) - len(set2)
        assert set(difference).isdisjoint(set(set2))


class TestAnalysisOperations:
    """Test analysis and statistics operations."""
    
    def test_is_valid_cell(self):
        """Test cell validation."""
        assert is_valid_cell(VALID_H3_CELL)
        assert not is_valid_cell("invalid_cell")
        assert not is_valid_cell("")
    
    def test_grid_statistics(self):
        """Test comprehensive grid statistics."""
        cells = grid_disk(VALID_H3_CELL, 1)
        stats = grid_statistics(cells)
        
        # Check for either 'total_cells' or 'cell_count' depending on implementation
        assert "total_cells" in stats or "cell_count" in stats
        cell_count = stats.get("total_cells", stats.get("cell_count", 0))
        assert cell_count == len(cells)
        
        assert "total_area_km2" in stats
        assert stats["total_area_km2"] > 0
        
        assert "unique_resolutions" in stats
        assert "connectivity_ratio" in stats
        assert "bounding_box" in stats
        
        # Bounding box should contain all cell centers
        bbox = stats["bounding_box"]
        for cell in cells:
            lat, lng = cell_to_coordinates(cell)
            assert bbox["min_lat"] <= lat <= bbox["max_lat"]
            assert bbox["min_lng"] <= lng <= bbox["max_lng"]
    
    def test_get_resolution_info(self):
        """Test getting resolution information."""
        info = get_resolution_info(9)
        
        assert info["resolution"] == 9
        assert "avg_edge_length_km" in info
        assert "avg_area_km2" in info
        assert "description" in info
        assert info["avg_edge_length_km"] > 0
        assert info["avg_area_km2"] > 0
    
    def test_find_optimal_resolution(self):
        """Test finding optimal resolution for area."""
        result = find_optimal_resolution(1.0)  # 1 km²
        
        assert "recommended_resolution" in result
        assert "estimated_cells" in result
        assert "all_options" in result
        
        assert 0 <= result["recommended_resolution"] <= 15
        assert result["estimated_cells"] > 0
        assert len(result["all_options"]) == 5
    
    def test_create_h3_grid_for_bounds(self):
        """Test creating H3 grid for bounding box."""
        min_lat, max_lat = SF_LAT - 0.01, SF_LAT + 0.01
        min_lng, max_lng = SF_LNG - 0.01, SF_LNG + 0.01
        
        grid = create_h3_grid_for_bounds(min_lat, max_lat, min_lng, max_lng, RESOLUTION)
        
        assert isinstance(grid, list)
        assert len(grid) > 0
        
        # All cells should be valid
        for cell in grid:
            assert is_valid_cell(cell)
            assert cell_resolution(cell) == RESOLUTION
        
        # All cell centers should be within bounds
        for cell in grid:
            lat, lng = cell_to_coordinates(cell)
            # Allow some tolerance for cells that partially overlap
            assert min_lat - 0.01 <= lat <= max_lat + 0.01
            assert min_lng - 0.01 <= lng <= max_lng + 0.01


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_h3_index(self):
        """Test handling of invalid H3 indices."""
        invalid_index = "invalid_h3_index"
        
        with pytest.raises(ValueError):
            cell_to_coordinates(invalid_index)
        
        with pytest.raises(ValueError):
            cell_to_boundary(invalid_index)
        
        assert not is_valid_cell(invalid_index)
    
    def test_empty_cell_sets(self):
        """Test handling of empty cell sets."""
        empty_set = set()
        
        assert cells_intersection(empty_set, {VALID_H3_CELL}) == []
        assert set(cells_union(empty_set, {VALID_H3_CELL})) == {VALID_H3_CELL}
        assert set(cells_difference({VALID_H3_CELL}, empty_set)) == {VALID_H3_CELL}
        
        stats = grid_statistics(empty_set)
        assert "error" in stats
    
    def test_invalid_bounds(self):
        """Test handling of invalid coordinate bounds."""
        with pytest.raises(ValueError):
            create_h3_grid_for_bounds(91, 90, 0, 1, 9)  # Invalid lat
        
        with pytest.raises(ValueError):
            create_h3_grid_for_bounds(0, 1, 181, 180, 9)  # Invalid lng
        
        with pytest.raises(ValueError):
            create_h3_grid_for_bounds(0, 1, 0, 1, 16)  # Invalid resolution


if __name__ == "__main__":
    pytest.main([__file__])
