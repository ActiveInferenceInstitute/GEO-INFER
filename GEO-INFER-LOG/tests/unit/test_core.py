"""
Unit tests for GEO-INFER-LOG core functionality.
"""

import pytest
import geopandas as gpd
from shapely.geometry import Point

from geo_infer_log import __version__


class TestLogModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_log
        assert geo_infer_log is not None

    def test_module_version(self) -> None:
        """Test that module has a version."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_module_structure(self) -> None:
        """Test that module has expected structure."""
        import geo_infer_log
        
        # Check that submodules exist
        assert hasattr(geo_infer_log, 'core')
        assert hasattr(geo_infer_log, 'api')
        assert hasattr(geo_infer_log, 'models')
        assert hasattr(geo_infer_log, 'utils')

    def test_routing_import(self) -> None:
        """Test that routing module can be imported."""
        from geo_infer_log.core.routing import RouteOptimizer

        assert RouteOptimizer is not None

