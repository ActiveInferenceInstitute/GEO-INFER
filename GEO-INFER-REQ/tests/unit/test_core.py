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
        """Test that module has expected core classes."""
        import geo_infer_req

        # Check that core classes are available
        assert hasattr(geo_infer_req, 'RequirementsAnalyzer')
        assert hasattr(geo_infer_req, 'TraceabilityManager')
        assert hasattr(geo_infer_req, 'RequirementValidator')

