"""
Unit tests for GEO-INFER-CIV core functionality.
"""

import pytest

from geo_infer_civ import __version__


class TestCivicModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_civ
        assert geo_infer_civ is not None

    def test_module_version(self) -> None:
        """Test that module has a version."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_module_structure(self) -> None:
        """Test that module has expected structure."""
        import geo_infer_civ
        
        # Check that submodules exist
        assert hasattr(geo_infer_civ, 'core')
        assert hasattr(geo_infer_civ, 'api')
        assert hasattr(geo_infer_civ, 'models')
        assert hasattr(geo_infer_civ, 'utils')

