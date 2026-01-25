"""
Comprehensive tests for enhanced H3 backend methods.

Tests for validation, utility, directed edge, coordinate, and geometric methods.
"""

import pytest
import numpy as np
from geo_infer_space.backends.h3.h3_backend import H3Backend


@pytest.fixture
def h3():
    """Create H3 backend instance."""
    return H3Backend()


@pytest.fixture
def sample_cell(h3):
    """Generate a sample H3 cell for San Francisco."""
    return h3.latlng_to_cell(37.7749, -122.4194, 8)


@pytest.fixture
def sample_cells(h3, sample_cell):
    """Generate a set of sample cells with neighbors."""
    neighbors = h3.get_cell_neighbors(sample_cell, k=1)
    return [sample_cell] + list(neighbors)


class TestValidation:
    """Tests for validation methods."""
    
    def test_is_valid_cell_valid(self, h3, sample_cell):
        """Test valid cell returns True."""
        assert h3.is_valid_cell(sample_cell) is True
    
    def test_is_valid_cell_invalid(self, h3):
        """Test invalid cell returns False."""
        assert h3.is_valid_cell("not_a_cell") is False
        assert h3.is_valid_cell("") is False
        assert h3.is_valid_cell("12345") is False
    
    def test_validate_resolution_valid(self, h3):
        """Test valid resolutions."""
        for res in range(16):
            result = h3.validate_resolution(res)
            assert result['valid'] is True
            assert result['resolution'] == res
            assert result['error'] is None
    
    def test_validate_resolution_invalid(self, h3):
        """Test invalid resolutions."""
        for res in [-1, 16, 100, -100]:
            result = h3.validate_resolution(res)
            assert result['valid'] is False
            assert result['error'] is not None
    
    def test_validate_resolution_non_integer(self, h3):
        """Test non-integer resolution."""
        result = h3.validate_resolution(5.5)
        assert result['valid'] is False
    
    def test_validate_coordinates_valid(self, h3):
        """Test valid coordinates."""
        result = h3.validate_coordinates(37.7749, -122.4194)
        assert result['valid'] is True
        assert result['lat_valid'] is True
        assert result['lng_valid'] is True
    
    def test_validate_coordinates_poles(self, h3):
        """Test coordinates at poles."""
        result = h3.validate_coordinates(90, 0)
        assert result['valid'] is True
        
        result = h3.validate_coordinates(-90, 0)
        assert result['valid'] is True
    
    def test_validate_coordinates_dateline(self, h3):
        """Test coordinates at dateline."""
        result = h3.validate_coordinates(0, 180)
        assert result['valid'] is True
        
        result = h3.validate_coordinates(0, -180)
        assert result['valid'] is True
    
    def test_validate_coordinates_invalid(self, h3):
        """Test invalid coordinates."""
        result = h3.validate_coordinates(91, 0)
        assert result['valid'] is False
        assert not result['lat_valid']
        
        result = h3.validate_coordinates(0, 181)
        assert result['valid'] is False
        assert not result['lng_valid']


class TestCellProperties:
    """Tests for cell property methods."""
    
    def test_are_neighbors_adjacent(self, h3, sample_cell):
        """Test adjacent cells are neighbors."""
        neighbors = h3.get_cell_neighbors(sample_cell, k=1)
        for neighbor in neighbors:
            assert h3.are_neighbors(sample_cell, neighbor) is True
    
    def test_are_neighbors_non_adjacent(self, h3, sample_cell):
        """Test non-adjacent cells are not neighbors."""
        # Get distant cell
        distant_cell = h3.latlng_to_cell(40.7128, -74.0060, 8)  # NYC
        assert h3.are_neighbors(sample_cell, distant_cell) is False
    
    def test_is_pentagon_hexagon(self, h3, sample_cell):
        """Test regular hexagon is not pentagon."""
        assert h3.is_pentagon(sample_cell) is False
    
    def test_is_pentagon_actual_pentagon(self, h3):
        """Test actual pentagon cell."""
        pentagons = h3.get_pentagons(8)
        for pentagon in pentagons[:3]:
            assert h3.is_pentagon(pentagon) is True
    
    def test_is_res_class_iii(self, h3):
        """Test resolution class detection."""
        # Odd resolutions are Class III
        cell_res1 = h3.latlng_to_cell(37.7749, -122.4194, 1)
        assert h3.is_res_class_iii(cell_res1) is True
        
        # Even resolutions are Class II
        cell_res2 = h3.latlng_to_cell(37.7749, -122.4194, 2)
        assert h3.is_res_class_iii(cell_res2) is False
    
    def test_get_base_cell(self, h3, sample_cell):
        """Test base cell extraction."""
        base = h3.get_base_cell(sample_cell)
        assert isinstance(base, int)
        assert 0 <= base <= 121
    
    def test_get_icosahedron_faces(self, h3, sample_cell):
        """Test icosahedron face retrieval."""
        faces = h3.get_icosahedron_faces(sample_cell)
        assert isinstance(faces, list)
        assert len(faces) >= 1
        for face in faces:
            assert 0 <= face <= 19


class TestPentagons:
    """Tests for pentagon-related methods."""
    
    def test_get_pentagons_count(self, h3):
        """Test that exactly 12 pentagons exist per resolution."""
        for res in [0, 5, 8, 15]:
            pentagons = h3.get_pentagons(res)
            assert len(pentagons) == 12
    
    def test_get_pentagons_are_valid(self, h3):
        """Test that all returned pentagons are valid cells."""
        pentagons = h3.get_pentagons(8)
        for pentagon in pentagons:
            assert h3.is_valid_cell(pentagon) is True
            assert h3.is_pentagon(pentagon) is True
    
    def test_get_pentagons_invalid_resolution(self, h3):
        """Test invalid resolution raises error."""
        with pytest.raises(ValueError):
            h3.get_pentagons(-1)
        with pytest.raises(ValueError):
            h3.get_pentagons(16)


class TestResolutionConversion:
    """Tests for resolution conversion methods."""
    
    def test_get_cells_at_resolution_same(self, h3, sample_cells):
        """Test cells at same resolution returned unchanged."""
        result = h3.get_cells_at_resolution(sample_cells, 8)
        assert len(result) == len(sample_cells)
    
    def test_get_cells_at_resolution_coarser(self, h3, sample_cells):
        """Test conversion to coarser resolution."""
        result = h3.get_cells_at_resolution(sample_cells, 5)
        assert all(h3.get_cell_resolution(c) == 5 for c in result)
        # Fewer cells at coarser resolution
        assert len(result) <= len(sample_cells)
    
    def test_get_cells_at_resolution_finer(self, h3, sample_cells):
        """Test conversion to finer resolution."""
        result = h3.get_cells_at_resolution(sample_cells[:1], 10)
        assert all(h3.get_cell_resolution(c) == 10 for c in result)
        # More cells at finer resolution
        assert len(result) > 1


class TestDirectedEdges:
    """Tests for directed edge methods."""
    
    def test_get_directed_edge(self, h3, sample_cell):
        """Test getting directed edge between neighbors."""
        neighbors = h3.get_cell_neighbors(sample_cell, k=1)
        edge = h3.get_directed_edge(sample_cell, neighbors[0])
        assert isinstance(edge, str)
        assert len(edge) > 0
    
    def test_get_directed_edge_non_neighbors(self, h3):
        """Test error for non-neighbor cells."""
        cell1 = h3.latlng_to_cell(37.7749, -122.4194, 8)
        cell2 = h3.latlng_to_cell(40.7128, -74.0060, 8)  # NYC
        with pytest.raises(ValueError):
            h3.get_directed_edge(cell1, cell2)
    
    def test_edge_to_cells(self, h3, sample_cell):
        """Test getting cells from edge."""
        neighbors = h3.get_cell_neighbors(sample_cell, k=1)
        edge = h3.get_directed_edge(sample_cell, neighbors[0])
        
        origin, destination = h3.edge_to_cells(edge)
        assert origin == sample_cell
        assert destination == neighbors[0]
    
    def test_get_cell_edges(self, h3, sample_cell):
        """Test getting all edges of a cell."""
        edges = h3.get_cell_edges(sample_cell)
        # Hexagon has 6 edges
        assert len(edges) == 6
    
    def test_get_cell_edges_pentagon(self, h3):
        """Test pentagon has 5 edges."""
        pentagons = h3.get_pentagons(8)
        edges = h3.get_cell_edges(pentagons[0])
        assert len(edges) == 5
    
    def test_get_edge_boundary(self, h3, sample_cell):
        """Test getting edge boundary."""
        edges = h3.get_cell_edges(sample_cell)
        boundary = h3.get_edge_boundary(edges[0])
        assert len(boundary) == 2  # Edge has 2 vertices
        for point in boundary:
            assert len(point) == 2  # lat, lng


class TestLocalIJCoordinates:
    """Tests for local IJ coordinate methods."""
    
    def test_cell_to_local_ij(self, h3, sample_cell):
        """Test converting cell to local IJ."""
        neighbors = h3.get_cell_neighbors(sample_cell, k=1)
        i, j = h3.cell_to_local_ij(sample_cell, neighbors[0])
        assert isinstance(i, int)
        assert isinstance(j, int)
    
    def test_local_ij_to_cell(self, h3, sample_cell):
        """Test converting local IJ back to cell."""
        neighbors = h3.get_cell_neighbors(sample_cell, k=1)
        i, j = h3.cell_to_local_ij(sample_cell, neighbors[0])
        
        result_cell = h3.local_ij_to_cell(sample_cell, i, j)
        assert result_cell == neighbors[0]
    
    def test_local_ij_roundtrip(self, h3, sample_cell):
        """Test IJ coordinate roundtrip."""
        neighbors = h3.get_cell_neighbors(sample_cell, k=2)
        for neighbor in neighbors[:5]:
            i, j = h3.cell_to_local_ij(sample_cell, neighbor)
            result = h3.local_ij_to_cell(sample_cell, i, j)
            assert result == neighbor


class TestGeometricCalculations:
    """Tests for geometric calculation methods."""
    
    def test_great_circle_distance_same_point(self, h3):
        """Test distance between same point is 0."""
        dist = h3.great_circle_distance(37.7749, -122.4194, 37.7749, -122.4194)
        assert dist == 0
    
    def test_great_circle_distance_known(self, h3):
        """Test distance for known locations."""
        # SF to NYC, approximately 4,130 km
        dist = h3.great_circle_distance(
            37.7749, -122.4194,  # SF
            40.7128, -74.0060,   # NYC
            unit='km'
        )
        assert 4000 < dist < 4200
    
    def test_great_circle_distance_units(self, h3):
        """Test distance unit conversion."""
        dist_m = h3.great_circle_distance(37.7749, -122.4194, 37.8, -122.4, unit='m')
        dist_km = h3.great_circle_distance(37.7749, -122.4194, 37.8, -122.4, unit='km')
        assert abs(dist_m / 1000 - dist_km) < 0.001
    
    def test_cell_to_geodesic_area(self, h3, sample_cell):
        """Test geodesic area calculation."""
        area = h3.cell_to_geodesic_area(sample_cell, unit='km^2')
        assert area > 0
        # Res 8 cell is roughly 0.7 - 0.9 km²
        assert 0.5 < area < 1.2
    
    def test_average_edge_length(self, h3):
        """Test average edge length at various resolutions."""
        for res in [0, 5, 8, 15]:
            length = h3.average_edge_length(res, unit='m')
            assert length > 0
        
        # Higher resolution = shorter edges
        len_res0 = h3.average_edge_length(0, unit='m')
        len_res15 = h3.average_edge_length(15, unit='m')
        assert len_res0 > len_res15
    
    def test_line_to_cells(self, h3):
        """Test line to cells conversion."""
        cells = h3.line_to_cells(
            37.7749, -122.4194,  # Start (SF)
            37.7849, -122.4094,  # End (nearby)
            resolution=8
        )
        assert len(cells) >= 2  # At least start and end
        for cell in cells:
            assert h3.is_valid_cell(cell) is True
    
    def test_point_distance_to_cell_center(self, h3, sample_cell):
        """Test point to cell center distance."""
        center = h3.cell_to_latlng(sample_cell)
        
        # Distance from center to itself should be 0
        dist = h3.point_distance_to_cell_center(center[0], center[1], sample_cell)
        assert dist < 1  # Less than 1 meter
    
    def test_get_resolution_stats(self, h3):
        """Test resolution statistics."""
        for res in [0, 8, 15]:
            stats = h3.get_resolution_stats(res)
            assert stats['resolution'] == res
            assert stats['num_pentagons'] == 12
            assert stats['total_cells'] > 0
            assert stats['average_area_km2'] > 0
            assert stats['average_edge_length_km'] > 0


class TestComprehensiveValidation:
    """Tests for comprehensive validation methods."""
    
    def test_validate_cell_set_all_valid(self, h3, sample_cells):
        """Test validation of all valid cells."""
        result = h3.validate_cell_set(sample_cells)
        assert result['all_valid'] is True
        assert result['valid_count'] == len(sample_cells)
        assert result['invalid_count'] == 0
    
    def test_validate_cell_set_with_invalid(self, h3, sample_cells):
        """Test validation with invalid cells."""
        mixed = sample_cells + ["invalid_cell", "bad"]
        result = h3.validate_cell_set(mixed)
        assert result['all_valid'] is False
        assert result['invalid_count'] == 2
        assert len(result['invalid_cells']) == 2
    
    def test_validate_cell_set_uniform_resolution(self, h3, sample_cells):
        """Test uniform resolution detection."""
        result = h3.validate_cell_set(sample_cells)
        assert result['is_uniform_resolution'] is True
        assert result['resolutions_present'] == [8]
    
    def test_validate_cell_set_mixed_resolution(self, h3, sample_cell):
        """Test mixed resolution detection."""
        # Get cells at different resolutions
        mixed = [
            h3.get_cell_parent(sample_cell, 5),
            sample_cell,
            h3.get_cell_children(sample_cell, 10)[0]
        ]
        result = h3.validate_cell_set(mixed)
        assert result['is_uniform_resolution'] is False
        assert len(result['resolutions_present']) == 3
    
    def test_validate_cell_set_with_pentagon(self, h3):
        """Test pentagon detection in cell set."""
        pentagons = h3.get_pentagons(8)
        regular = h3.latlng_to_cell(37.7749, -122.4194, 8)
        mixed = [regular, pentagons[0]]
        
        result = h3.validate_cell_set(mixed)
        assert result['pentagon_count'] == 1
        assert len(result['pentagons']) == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_cells_at_poles(self, h3):
        """Test cells at geographic poles."""
        # North pole
        cell_north = h3.latlng_to_cell(89.999, 0, 8)
        assert h3.is_valid_cell(cell_north) is True
        
        # South pole
        cell_south = h3.latlng_to_cell(-89.999, 0, 8)
        assert h3.is_valid_cell(cell_south) is True
    
    def test_cells_at_dateline(self, h3):
        """Test cells at international dateline."""
        cell_east = h3.latlng_to_cell(0, 179.999, 8)
        cell_west = h3.latlng_to_cell(0, -179.999, 8)
        assert h3.is_valid_cell(cell_east) is True
        assert h3.is_valid_cell(cell_west) is True
    
    def test_empty_cell_list(self, h3):
        """Test validation of empty cell list."""
        result = h3.validate_cell_set([])
        assert result['total_cells'] == 0
        assert result['all_valid'] is True
