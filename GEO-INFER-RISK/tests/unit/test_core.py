"""
Unit tests for GEO-INFER-RISK core functionality.
"""

import tomllib
from pathlib import Path

from geo_infer_risk import __license__, __version__, create_risk_analysis


class TestRiskModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_risk

        assert geo_infer_risk is not None

    def test_module_metadata_matches_pyproject(self) -> None:
        """Runtime version and license match authoritative project metadata."""
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]

        assert __version__ == project["version"]
        assert __license__ == project["license"]

    def test_module_structure(self) -> None:
        """Test that module has expected structure."""
        import geo_infer_risk

        # Check that core components exist
        assert hasattr(geo_infer_risk, "core")
        assert hasattr(geo_infer_risk, "create_risk_analysis")

    def test_risk_analysis_creation(self) -> None:
        """Test creating a risk analysis engine."""
        engine = create_risk_analysis()
        assert engine is not None
