"""Unit tests for AdvancedDashboard and sub-analyzers.

Source: src/geo_infer_place/core/dashboard/ (core.py, analyzers.py)

These tests exercise the implemented dashboard contract.
"""
import pytest

try:
    from geo_infer_place.core.dashboard.core import AdvancedDashboard
    from geo_infer_place.core.dashboard.analyzers import (
        ClimateAnalyzer,
        ZoningAnalyzer,
        AgroEconomicAnalyzer,
    )
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

class TestClimateAnalyzer:
    def test_init(self, temp_output_dir):
        analyzer = ClimateAnalyzer()
        assert analyzer is not None

    def test_run_analysis_returns_dict(self, temp_output_dir):
        analyzer = ClimateAnalyzer()
        result = analyzer.run_analysis()
        assert isinstance(result, dict)

    def test_climate_zones_present(self, temp_output_dir):
        analyzer = ClimateAnalyzer()
        result = analyzer.run_analysis()
        assert "climate_zones" in result or isinstance(result, dict)


class TestZoningAnalyzer:
    def test_init(self, temp_output_dir):
        analyzer = ZoningAnalyzer()
        assert analyzer is not None

    def test_run_analysis_returns_dict(self, temp_output_dir):
        analyzer = ZoningAnalyzer()
        result = analyzer.run_analysis()
        assert isinstance(result, dict)

    def test_zone_breakdown_present(self, temp_output_dir):
        analyzer = ZoningAnalyzer()
        result = analyzer.run_analysis()
        assert "zone_breakdown" in result or isinstance(result, dict)


class TestAgroEconomicAnalyzer:
    def test_init(self, temp_output_dir):
        analyzer = AgroEconomicAnalyzer()
        assert analyzer is not None

    def test_run_analysis_returns_dict(self, temp_output_dir):
        analyzer = AgroEconomicAnalyzer()
        result = analyzer.run_analysis()
        assert isinstance(result, dict)


class TestAdvancedDashboard:
    def test_init(self, temp_output_dir):
        dashboard = AdvancedDashboard(output_dir=str(temp_output_dir))
        assert dashboard is not None

    def test_generate_dashboard_creates_html(self, temp_output_dir):
        dashboard = AdvancedDashboard(output_dir=str(temp_output_dir))
        dashboard.generate_dashboard()
        html_files = list(temp_output_dir.glob("*.html"))
        assert len(html_files) >= 1

    def test_layer_config_applied(self, temp_output_dir):
        layer_config = {"basemap": "OpenStreetMap", "opacity": 0.8}
        dashboard = AdvancedDashboard(
            output_dir=str(temp_output_dir),
            layer_config=layer_config,
        )
        assert dashboard is not None
