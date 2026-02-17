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
        """Test that module has expected core classes."""
        import geo_infer_civ

        # Check that core classes are available
        assert hasattr(geo_infer_civ, 'ParticipationAnalyzer')
        assert hasattr(geo_infer_civ, 'AttendanceTracker')
        assert hasattr(geo_infer_civ, 'CostBenefitAnalyzer')

