#!/usr/bin/env python3
"""
Tests for GEO-INFER-PLACE H3 spatial operations.

Validates latlng_to_cell, cell_to_latlng, polygon_to_cells,
grid_disk, is_valid_cell, and GeoDataFrame conversion.
"""

import pytest
import numpy as np

from geo_infer_place.utils.h3_operations import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_latlng_boundary,
    polygon_to_cells,
    grid_disk,
    grid_distance,
    cell_area,
    get_resolution,
    is_valid_cell,
    are_neighbor_cells,
    cells_to_geodataframe,
    geo_to_cells,
)


# -- latlng_to_cell / cell_to_latlng round-trip --------------------------

class TestLatLngConversion:
    """Test H3 cell ↔ lat/lng conversions."""

    def test_round_trip_preserves_locality(self):
        """Forward→reverse should return a point within the same cell."""
        lat, lng = 41.75, -124.2
        cell = latlng_to_cell(lat, lng, 8)
        rlat, rlng = cell_to_latlng(cell)
        # Reverse point should be close (within ~0.05 degree for res 8)
        assert abs(rlat - lat) < 0.1
        assert abs(rlng - lng) < 0.1

    def test_resolution_affects_cell_id(self):
        """Different resolutions should yield different cell IDs."""
        lat, lng = 41.75, -124.2
        cell_low = latlng_to_cell(lat, lng, 4)
        cell_high = latlng_to_cell(lat, lng, 10)
        assert cell_low != cell_high

    def test_cell_boundary_returns_coordinates(self):
        """cell_to_latlng_boundary should return a sequence of coordinate pairs."""
        cell = latlng_to_cell(41.75, -124.2, 8)
        boundary = cell_to_latlng_boundary(cell)
        assert len(boundary) >= 5  # Hexagons + closure
        for coord in boundary:
            assert len(coord) == 2


# -- polygon_to_cells & geo_to_cells -------------------------------------

class TestPolygonToCells:
    """Test polygon→H3 cell conversion."""

    def test_small_polygon_returns_cells(self):
        """A small polygon should return at least one H3 cell."""
        geojson = {
            "type": "Polygon",
            "coordinates": [[
                [-124.25, 41.70],
                [-124.15, 41.70],
                [-124.15, 41.80],
                [-124.25, 41.80],
                [-124.25, 41.70],
            ]]
        }
        cells = polygon_to_cells(geojson, 8)
        assert len(cells) > 0
        for c in cells:
            assert is_valid_cell(c)

    def test_geo_to_cells_accepts_geojson(self):
        """geo_to_cells wrapper should also work."""
        geojson = {
            "type": "Polygon",
            "coordinates": [[
                [-124.25, 41.70],
                [-124.15, 41.70],
                [-124.15, 41.80],
                [-124.25, 41.80],
                [-124.25, 41.70],
            ]]
        }
        cells = geo_to_cells(geojson, 6)
        assert len(cells) > 0


# -- grid operations ------------------------------------------------------

class TestGridOperations:
    """Test grid_disk, grid_distance, cell_area, etc."""

    def test_grid_disk_returns_neighbors(self):
        """Grid disk of radius 1 should return ≥ 7 cells (center + ring)."""
        center = latlng_to_cell(41.75, -124.2, 8)
        disk = grid_disk(center, 1)
        assert len(disk) >= 7
        assert center in disk

    def test_grid_distance_self_is_zero(self):
        """Distance from a cell to itself should be 0."""
        cell = latlng_to_cell(41.75, -124.2, 8)
        assert grid_distance(cell, cell) == 0

    def test_cell_area_positive(self):
        """Cell area should be positive."""
        cell = latlng_to_cell(41.75, -124.2, 8)
        area = cell_area(cell)
        assert area > 0

    def test_get_resolution(self):
        """get_resolution should return the resolution used to create the cell."""
        for res in (4, 8, 12):
            cell = latlng_to_cell(41.75, -124.2, res)
            assert get_resolution(cell) == res


# -- validity & neighbor checks -------------------------------------------

class TestValidity:
    """Test is_valid_cell and are_neighbor_cells."""

    def test_valid_cell(self):
        cell = latlng_to_cell(41.75, -124.2, 8)
        assert is_valid_cell(cell)

    def test_invalid_cell(self):
        assert not is_valid_cell("not_a_cell")

    def test_neighbors_are_neighbors(self):
        center = latlng_to_cell(41.75, -124.2, 8)
        disk = list(grid_disk(center, 1))
        for c in disk:
            if c != center:
                assert are_neighbor_cells(center, c) or grid_distance(center, c) == 1


# -- GeoDataFrame conversion ---------------------------------------------

class TestCellsToGeoDataFrame:
    """Test cells_to_geodataframe utility."""

    def test_returns_geodataframe(self):
        cells = list(grid_disk(latlng_to_cell(41.75, -124.2, 8), 1))
        gdf = cells_to_geodataframe(cells)
        assert len(gdf) == len(cells)
        assert "geometry" in gdf.columns
        assert "h3_cell" in gdf.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
