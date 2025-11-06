"""
Unit tests for GEO-INFER-ORG core functionality.
"""

import pytest


class TestOrgModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_org
        assert geo_infer_org is not None

    def test_module_structure(self) -> None:
        """Test that module has expected structure."""
        import geo_infer_org
        
        # Check that submodules exist
        assert hasattr(geo_infer_org, 'core')
        assert hasattr(geo_infer_org, 'api')
        assert hasattr(geo_infer_org, 'models')
        assert hasattr(geo_infer_org, 'utils')

