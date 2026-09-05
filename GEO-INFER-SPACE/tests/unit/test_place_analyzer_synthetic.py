"""Tests for PlaceAnalyzer synthetic demo mode (geo_infer_space.place_analyzer)."""

import logging

import pytest

from geo_infer_space.place_analyzer import PlaceAnalyzer


@pytest.fixture()
def analyzer(tmp_path):
    return PlaceAnalyzer(base_dir=str(tmp_path / "base"))


class TestSyntheticDemoMode:
    def test_synthetic_data_is_labelled(self, analyzer):
        results = analyzer.analyze_place("Demo", (40.7128, -74.0060), radius_km=5)
        assert results["synthetic"] is True
        assert (
            results["environmental_factors"]["data_provenance"] == "synthetic_demo"
        )
        assert (
            results["accessibility_metrics"]["data_provenance"] == "synthetic_demo"
        )

    def test_synthetic_mode_logs_warning(self, analyzer, caplog):
        with caplog.at_level(logging.WARNING, logger="geo_infer_space.place_analyzer"):
            analyzer.analyze_place("Demo", (40.7128, -74.0060), radius_km=5)
        assert any("SYNTHETIC" in r.message for r in caplog.records)

    def test_synthetic_scores_excluded_from_summary(self, analyzer):
        analyzer.analyze_place("Demo", (40.7128, -74.0060), radius_km=5)
        summary = analyzer.get_analysis_summary("Demo")
        assert summary["synthetic"] is True
        assert summary["environmental_score"] is None
        assert summary["accessibility_score"] is None
        assert "synthetic" in summary["note"]

    def test_synthetic_false_skips_fabricated_sections(self, analyzer):
        results = analyzer.analyze_place(
            "Real", (40.7128, -74.0060), radius_km=5, synthetic=False
        )
        assert "environmental_factors" not in results
        assert "accessibility_metrics" not in results
        summary = analyzer.get_analysis_summary("Real")
        assert summary["environmental_score"] is None
        assert summary["accessibility_score"] is None

    def test_synthetic_generation_is_deterministic(self, analyzer):
        first = analyzer.analyze_place("A", (40.7128, -74.0060), radius_km=5)
        second = analyzer.analyze_place("B", (40.7128, -74.0060), radius_km=5)
        assert (
            first["environmental_factors"]["vegetation_cover"]
            == second["environmental_factors"]["vegetation_cover"]
        )

    def test_spatial_metrics_still_real(self, analyzer):
        """Spatial metrics (H3 cells, geometry) are real regardless of mode."""
        results = analyzer.analyze_place("Geo", (40.7128, -74.0060), radius_km=5)
        assert len(results["h3_cells"]) > 0
        assert results["spatial_metrics"]["area_km2"] > 0

    def test_new_base_dir_created(self, tmp_path):
        """base_dir that does not exist yet must be created (parents included)."""
        base = tmp_path / "new" / "nested"
        PlaceAnalyzer(base_dir=str(base))
        assert (base / "data").is_dir()
        assert (base / "config").is_dir()