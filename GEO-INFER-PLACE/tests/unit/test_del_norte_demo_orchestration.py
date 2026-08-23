#!/usr/bin/env python3
"""
Unit tests for the Del Norte County demo orchestration helpers.

Covers the standalone ``run_analysis.py`` script surfaces that the demo
pipeline (create_del_norte_dashboard.py / del_norte_county_demo.py /
run_analysis.py) depends on:

- load_location_config() returns valid Del Norte bounds + spatial config.
- cleanup_old_results() keeps only the most recent generated result per
  type and removes stale combined dashboards / analysis JSON files.

These are pure, deterministic logic paths exercised without a network.
"""
from __future__ import annotations

import importlib.util
from datetime import datetime
from pathlib import Path
from types import ModuleType

import pytest

PLACE_DIR = Path(__file__).resolve().parents[2]
RUN_ANALYSIS = PLACE_DIR / "locations" / "del_norte_county" / "run_analysis.py"


def _load_run_analysis() -> ModuleType:
    """Load run_analysis.py by path as an importable module."""
    spec = importlib.util.spec_from_file_location(
        "del_norte_run_analysis", RUN_ANALYSIS
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def run_analysis() -> ModuleType:
    return _load_run_analysis()


class TestLoadLocationConfig:
    def test_returns_location_section(self, run_analysis):
        config = run_analysis.load_location_config()
        assert "location" in config
        bounds = config["location"]["bounds"]
        assert bounds["west"] < bounds["east"]  # lon ordering for CA coast
        assert bounds["south"] < bounds["north"]

    def test_bounds_match_del_norte_extent(self, run_analysis):
        config = run_analysis.load_location_config()
        bounds = config["location"]["bounds"]
        assert abs(bounds["east"] + 123.536) < 0.01  # Crescent City environs
        assert abs(bounds["west"] + 124.408) < 0.01  # Pacific boundary

    def test_returns_analyses_section(self, run_analysis):
        config = run_analysis.load_location_config()
        assert "analyses" in config
        for analysis in (
            "forest_health",
            "coastal_resilience",
            "fire_risk",
        ):
            assert analysis in config["analyses"], (
                f"analysis '{analysis}' missing from config"
            )


class TestCleanupOldResults:
    @staticmethod
    def _ts(day: int) -> str:
        """Build a timestamp string in the %Y%m%d_%H%M%S format."""
        return datetime(2026, 1, day, 12, 30, 15).strftime("%Y%m%d_%H%M%S")

    def test_keeps_most_recent_dashboard(self, run_analysis, tmp_path):
        older = tmp_path / f"del_norte_intelligence_dashboard_{self._ts(1)}.html"
        newer = tmp_path / f"del_norte_intelligence_dashboard_{self._ts(2)}.html"
        older.write_text("<html>older</html>")
        newer.write_text("<html>newer</html>")

        run_analysis.cleanup_old_results(tmp_path)

        assert older.exists() is False, "older dashboard should be removed"
        assert newer.exists() is True, "newest dashboard should be kept"

    def test_keeps_most_recent_combined_results(self, run_analysis, tmp_path):
        older = tmp_path / f"del_norte_combined_results_{self._ts(1)}.json"
        newer = tmp_path / f"del_norte_combined_results_{self._ts(3)}.json"
        older.write_text("{}")
        newer.write_text("{}")

        run_analysis.cleanup_old_results(tmp_path)

        assert not older.exists()
        assert newer.exists()

    def test_preserves_non_timestamped_files(self, run_analysis, tmp_path):
        keep = tmp_path / "README.md"
        keep.write_text("# keep me")
        run_analysis.cleanup_old_results(tmp_path)
        assert keep.exists()

    def test_empty_dir_is_noop(self, run_analysis, tmp_path):
        run_analysis.cleanup_old_results(tmp_path)
        assert list(tmp_path.iterdir()) == []

    def test_handles_missing_dir_gracefully(self, run_analysis, tmp_path):
        missing = tmp_path / "does_not_exist"
        # Should not raise even though the directory is absent.
        run_analysis.cleanup_old_results(missing)


class TestDelNorteDemoFlow:
    """End-to-end demo pipeline (load_configuration -> comprehensive analysis).

    Mirrors del_norte_county_demo.py's ordering: load_configuration() first,
    then run_comprehensive_analysis() and generate_comprehensive_dashboard().
    Uses the real analyzers so the integration is exercised, not mocked.
    """

    @pytest.fixture()
    def dashboard(self, tmp_path):
        from geo_infer_place.locations.del_norte_county.comprehensive_dashboard import (
            DelNorteComprehensiveDashboard,
        )

        out = tmp_path / "demo_flow"
        d = DelNorteComprehensiveDashboard(output_dir=str(out))
        d.load_configuration()
        return d

    def test_load_configuration_populates_bounds(self, dashboard):
        bbox = dashboard.location_bounds.to_bbox()
        west, south, east, north = bbox
        assert west < east and south < north
        assert west < 0 and east < 0  # CA west coast longitudes

    def test_run_comprehensive_analysis_returns_all_domains(self, dashboard):
        results = dashboard.run_comprehensive_analysis()
        for domain in (
            "forest_health",
            "coastal_resilience",
            "fire_risk",
            "integration",
            "h3_aggregation",
        ):
            assert domain in results, f"missing domain: {domain}"

    def test_generate_comprehensive_dashboard_writes_html(self, dashboard):
        dashboard.run_comprehensive_analysis()
        html = dashboard.generate_comprehensive_dashboard()
        assert html and Path(html).exists()
        assert Path(html).stat().st_size > 1000

    def test_export_analysis_results_writes_json(self, dashboard):
        dashboard.run_comprehensive_analysis()
        path = dashboard.export_analysis_results()
        assert path and Path(path).exists()