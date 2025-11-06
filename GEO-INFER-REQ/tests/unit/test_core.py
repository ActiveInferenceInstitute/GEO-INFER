"""
Unit tests for GEO-INFER-REQ core functionality.
"""

import pytest


class TestReqModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_req
        assert geo_infer_req is not None

    def test_module_structure(self) -> None:
        """Test that module has expected structure."""
        import geo_infer_req
        
        # Check that submodules exist
        assert hasattr(geo_infer_req, 'core')
        assert hasattr(geo_infer_req, 'api')
        assert hasattr(geo_infer_req, 'models')
        assert hasattr(geo_infer_req, 'utils')

