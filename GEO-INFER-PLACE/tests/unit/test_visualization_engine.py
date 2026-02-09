#!/usr/bin/env python3
"""
Tests for GEO-INFER-PLACE InteractiveVisualizationEngine.

Validates engine initialization, layer group creation,
dashboard generation, and monitoring site data generation.
"""

import tempfile
from pathlib import Path

import pytest

from geo_infer_place.core.visualization_engine import InteractiveVisualizationEngine


@pytest.fixture
def location_config():
    """Minimal location config for testing."""
    return {
        "location": {
            "name": "Del Norte County",
            "bounds": {
                "north": 42.006,
                "south": 41.458,
                "east": -123.536,
                "west": -124.408,
            },
        }
    }


@pytest.fixture
def engine(location_config, tmp_path):
    """Create a visualization engine pointing at a temp output dir."""
    return InteractiveVisualizationEngine(
        location_config=location_config,
        output_dir=tmp_path,
        h3_resolution=8,
    )


class TestEngineInitialization:
    """Test viz engine init and configuration."""

    def test_creates_output_dir(self, engine, tmp_path):
        assert tmp_path.exists()

    def test_center_coordinates(self, engine):
        # Center of (42.006+41.458)/2 ≈ 41.732
        assert abs(engine.center_lat - 41.732) < 0.01
        assert abs(engine.center_lon - (-123.972)) < 0.01

    def test_h3_resolution(self, engine):
        assert engine.h3_resolution == 8


class TestLayerGroups:
    """Test layer group creation."""

    def test_creates_expected_groups(self, engine):
        groups = engine._create_layer_groups()
        expected = {
            "h3_grid",
            "forest_health",
            "coastal_resilience",
            "fire_risk",
            "community_development",
            "integration",
        }
        assert set(groups.keys()) == expected


class TestMonitoringSites:
    """Test data-driven monitoring site generators."""

    def test_forest_sites_fallback(self, engine):
        """Without analysis data, uses H3-grid fallback (5×4 = 20 sites)."""
        sites = engine._generate_forest_monitoring_sites()
        assert len(sites) == 20
        for site in sites:
            assert "site_id" in site
            assert "health_index" in site
            assert 0 <= site["health_index"] <= 1.0

    def test_forest_sites_from_data(self, engine):
        """With forest analysis data, extracts real plots."""
        data = {
            "data_acquisition": {
                "data_sources": {
                    "forest_inventory": {
                        "forest_plots": [
                            {"plot_id": "P01", "lat": 41.75, "lon": -124.1, "canopy_cover_percent": 80, "health_rating": "Good"},
                            {"plot_id": "P02", "lat": 41.80, "lon": -124.0, "ndvi": 0.72, "health_rating": "Excellent"},
                        ]
                    }
                }
            }
        }
        sites = engine._generate_forest_monitoring_sites(data)
        assert len(sites) == 2
        assert sites[0]["site_id"] == "P01"
        assert sites[1]["health_index"] == 0.9  # Excellent

    def test_coastal_sites_fallback(self, engine):
        """Without data, returns 10 real Del Norte coastal reference points."""
        sites = engine._generate_coastal_monitoring_sites()
        assert len(sites) == 10
        for site in sites:
            assert "vulnerability" in site

    def test_fire_sites_fallback(self, engine):
        """Without data, returns 10 known fire-relevant locations."""
        sites = engine._generate_fire_monitoring_sites()
        assert len(sites) == 10
        for site in sites:
            assert "risk_level" in site

    def test_community_facilities(self, engine):
        """Returns real verified Del Norte County facilities."""
        facilities = engine._generate_community_facilities()
        assert len(facilities) >= 8
        types = {f["type"] for f in facilities}
        assert "healthcare" in types
        assert "education" in types
        # Verify real facility name
        names = {f["name"] for f in facilities}
        assert "Sutter Coast Hospital" in names

    def test_h3_integration_grid_fallback(self, engine):
        """H3 grid without domain data produces zero-scored cells."""
        grid = engine._generate_h3_integration_grid({})
        assert len(grid) > 0
        for cell_data in grid.values():
            assert cell_data["integration_score"] == 0.0
            assert cell_data["domain_count"] == 0


class TestDashboardGeneration:
    """Test comprehensive dashboard generation."""

    def test_generates_html_file(self, engine, tmp_path):
        """Dashboard generation should produce an HTML file."""
        analysis_results = {
            "domain_results": {
                "forest_health": {"ndvi_mean": 0.65},
                "coastal_resilience": {"vulnerability": 0.4},
                "fire_risk": {"risk_score": 0.55},
            }
        }
        path = engine.create_comprehensive_dashboard(analysis_results)
        assert Path(path).exists()
        assert path.endswith(".html")
        # File should have real content
        assert Path(path).stat().st_size > 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
