"""Unit tests for DelNorteComprehensiveDashboard.

Source: src/geo_infer_place/core/comprehensive_dashboard.py

These tests are skipped if the module is not yet implemented.
"""
import pytest

try:
    from geo_infer_place.core.comprehensive_dashboard import DelNorteComprehensiveDashboard
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(
    not _HAS_MODULE,
    reason="geo_infer_place.core.comprehensive_dashboard not yet implemented",
)


class TestDelNorteComprehensiveDashboard:
    def test_init(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        assert dashboard is not None

    def test_run_analysis_returns_dict(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert isinstance(result, dict)

    def test_run_analysis_has_forest_health_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "forest_health" in result

    def test_run_analysis_has_coastal_resilience_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "coastal_resilience" in result

    def test_run_analysis_has_fire_risk_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "fire_risk" in result

    def test_run_analysis_has_seismic_hazard_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "seismic_hazard" in result

    def test_cross_domain_integrated_risk_present(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "integrated_risk" in result or any(
            "integrated" in str(k).lower() for k in result
        )

    def test_map_html_file_created(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        dashboard.run_analysis()
        html_files = list(temp_output_dir.glob("*.html"))
        assert len(html_files) >= 1
