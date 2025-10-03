"""
Tests for H3 Backend functionality.
"""

import pytest
from geo_infer_space.backends.h3 import H3Backend


class TestH3Backend:
    """Test the H3 backend implementation."""

    def test_backend_creation(self):
        """Test that H3 backend can be created."""
        backend = H3Backend()
        assert backend.name == "h3"
        assert backend.is_available() in [True, False]  # Can be either depending on h3 availability

    def test_backend_capabilities(self):
        """Test that backend reports correct capabilities."""
        backend = H3Backend()
        capabilities = backend.get_capabilities()

        assert 'indexing' in capabilities
        assert 'analytics' in capabilities
        assert 'supported_resolutions' in capabilities
        assert isinstance(capabilities['supported_resolutions'], list)

    def test_latlng_to_cell_mock(self):
        """Test latlng to cell conversion with mock implementation."""
        backend = H3Backend()

        # Test with mock coordinates
        cell = backend.latlng_to_cell(37.7749, -122.4194, 9)
        assert isinstance(cell, str)
        assert len(cell) > 0

    def test_cell_to_latlng_mock(self):
        """Test cell to latlng conversion with mock implementation."""
        backend = H3Backend()

        # Test with mock cell
        lat, lng = backend.cell_to_latlng("test_cell")
        assert isinstance(lat, float)
        assert isinstance(lng, float)

    def test_polygon_to_cells_mock(self):
        """Test polygon to cells conversion with mock implementation."""
        backend = H3Backend()

        polygon = {
            "type": "Polygon",
            "coordinates": [[
                [-122.42, 37.77], [-122.41, 37.77],
                [-122.41, 37.78], [-122.42, 37.78],
                [-122.42, 37.77]
            ]]
        }

        cells = backend.polygon_to_cells(polygon, 9)
        assert isinstance(cells, list)

    def test_hotspot_analysis_mock(self):
        """Test hotspot analysis with mock implementation."""
        backend = H3Backend()

        data = {
            'cells': ['cell1', 'cell2', 'cell3'],
            'values': [10, 50, 5]
        }

        result = backend.analyze_hotspots(data)
        assert 'hotspots' in result
        assert 'total_cells' in result
        assert 'hotspot_count' in result

    def test_proximity_analysis_mock(self):
        """Test proximity analysis with mock implementation."""
        backend = H3Backend()

        points = [
            (37.7749, -122.4194),
            (37.7849, -122.4094),
            (37.7649, -122.4294)
        ]

        result = backend.compute_proximity(points)
        assert 'proximity_pairs' in result
        assert 'total_points' in result
        assert 'analyzed_pairs' in result
