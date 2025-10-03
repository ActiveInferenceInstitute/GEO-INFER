"""
Tests for SRAI Backend functionality.
"""

import pytest
from geo_infer_space.backends.srai import SraiBackend


class TestSraiBackend:
    """Test the SRAI backend implementation."""

    def test_backend_creation(self):
        """Test that SRAI backend can be created."""
        backend = SraiBackend()
        assert backend.name == "srai"
        assert backend.is_available() in [True, False]  # Can be either depending on srai availability

    def test_backend_capabilities(self):
        """Test that backend reports correct capabilities."""
        backend = SraiBackend()
        capabilities = backend.get_capabilities()

        assert 'indexing' in capabilities
        assert 'analytics' in capabilities
        assert 'regionalizers' in capabilities
        assert isinstance(capabilities['regionalizers'], list)

    def test_latlng_to_cell_mock(self):
        """Test latlng to cell conversion with mock implementation."""
        backend = SraiBackend()

        # Test with mock coordinates
        cell = backend.latlng_to_cell(37.7749, -122.4194, 9)
        assert isinstance(cell, str)
        assert len(cell) > 0

    def test_cell_to_latlng_mock(self):
        """Test cell to latlng conversion with mock implementation."""
        backend = SraiBackend()

        # Test with mock cell
        lat, lng = backend.cell_to_latlng("test_cell")
        assert isinstance(lat, float)
        assert isinstance(lng, float)

    def test_polygon_to_cells_mock(self):
        """Test polygon to cells conversion with mock implementation."""
        backend = SraiBackend()

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
        backend = SraiBackend()

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
        backend = SraiBackend()

        points = [
            (37.7749, -122.4194),
            (37.7849, -122.4094),
            (37.7649, -122.4294)
        ]

        result = backend.compute_proximity(points)
        assert 'proximity_pairs' in result
        assert 'total_points' in result
        assert 'analyzed_pairs' in result

    def test_regionalizer_types(self):
        """Test that different regionalizer types are supported."""
        backend = SraiBackend(default_regionalizer='h3')
        assert backend.default_regionalizer == 'h3'

        backend_s2 = SraiBackend(default_regionalizer='s2')
        assert backend_s2.default_regionalizer == 's2'
