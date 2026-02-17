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
        """Test that module has expected core classes."""
        import geo_infer_org

        # Check that core classes are available
        assert hasattr(geo_infer_org, 'OrganizationModel')
        assert hasattr(geo_infer_org, 'VotingEngine')
        assert hasattr(geo_infer_org, 'CollaborationNetwork')

