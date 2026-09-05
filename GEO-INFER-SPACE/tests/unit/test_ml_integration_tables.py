"""
Tests for H3PerformanceOptimizer resolution tables backed by the real H3 API.

The optimizer previously hardcoded approximate per-resolution areas and edge
lengths. These tests pin the behavior now that values are computed from the
h3.average_hexagon_area / h3.average_hexagon_edge_length APIs.
"""

import h3
import pytest

from geo_infer_space.backends.h3.core import H3Cell, H3Grid
from geo_infer_space.backends.h3.ml_integration import H3DisasterResponse, H3PerformanceOptimizer


@pytest.fixture
def optimizer() -> H3PerformanceOptimizer:
    """Create performance optimizer instance."""
    return H3PerformanceOptimizer()


class TestResolutionRecommendation:
    """Tests for optimize_grid_resolution backed by real H3 statistics."""

    def test_recommendation_areas_match_h3_api(self, optimizer):
        """Every recommendation's cell area/edge length matches the H3 API."""
        result = optimizer.optimize_grid_resolution(100.0)

        assert "error" not in result
        for rec in result["all_recommendations"]:
            resolution = rec["resolution"]
            assert rec["avg_cell_area_km2"] == pytest.approx(
                h3.average_hexagon_area(resolution, unit="km^2"), rel=1e-9
            )
            assert rec["edge_length_km"] == pytest.approx(
                h3.average_hexagon_edge_length(resolution, unit="km"), rel=1e-9
            )

    def test_recommended_resolution_for_known_area(self, optimizer):
        """A known area resolves to a resolution whose area matches the API."""
        area_km2 = 100.0
        result = optimizer.optimize_grid_resolution(area_km2, analysis_type="ml")

        recommended = result["recommended_resolution"]
        assert 0 <= recommended <= 15

        area = h3.average_hexagon_area(recommended, unit="km^2")
        assert result["estimated_cells"] == int(area_km2 / area)
        assert result["estimated_cells"] > 0

    def test_estimated_cells_use_real_areas(self, optimizer):
        """estimated_cells is derived from the real average hexagon area."""
        area_km2 = 36.129
        result = optimizer.optimize_grid_resolution(area_km2)

        for rec in result["all_recommendations"]:
            expected = int(area_km2 / h3.average_hexagon_area(rec["resolution"], unit="km^2"))
            assert rec["estimated_cells"] == expected


class TestEvacuationZones:
    """Tests for evacuation zone calculation with real edge lengths."""

    @pytest.fixture
    def res9_grid(self):
        """Build a minimal grid at resolution 9 (not 6-8) around a hazard cell."""
        hazard = h3.latlng_to_cell(37.7749, -122.4194, 9)
        neighbor_cells = list(h3.grid_disk(hazard, 2))
        cells = []
        for idx in neighbor_cells:
            properties = {"population": 100.0}
            if idx == hazard:
                properties["flood_risk"] = 0.9
            cells.append(H3Cell(index=idx, resolution=9, properties=properties))
        return H3Grid(cells=cells, name="evac-test")

    def test_evacuation_zone_nontrivial_at_res9(self, res9_grid):
        """A res-9 hazard cell yields many rings since edge length is ~0.17 km."""
        analyzer = H3DisasterResponse(res9_grid)
        zones = analyzer.analyze_evacuation_zones(
            "flood_risk", evacuation_radius_km=1.0
        )

        assert "error" not in zones
        assert len(zones["high_risk_zones"]) == 1
        assert zones["high_risk_zones"][0]["cell_index"] == h3.latlng_to_cell(
            37.7749, -122.4194, 9
        )

        zone = zones["evacuation_zones"][0]
        assert "error" not in zone
        # 1 km radius at ~0.17 km edge length spans several rings; a trivial
        # hardcoded fallback (1.0 km default edge) would produce at most 2 rings.
        assert zone["zone_area_cells"] > 7
        # Cells within ring 2 of the hazard exist in the grid.
        assert len(zone["evacuation_cells"]) > 1

    def test_evacuation_zone_population_total(self, res9_grid):
        """Population sums across all grid cells inside the evacuation zone."""
        analyzer = H3DisasterResponse(res9_grid)
        zones = analyzer.analyze_evacuation_zones(
            "flood_risk", evacuation_radius_km=0.5
        )

        assert "error" not in zones
        zone = zones["evacuation_zones"][0]
        # Only cells present in the grid contribute population (100 each).
        assert zone["total_population"] == 100.0 * len(zone["evacuation_cells"])
        assert zones["total_affected_population"] == zone["total_population"]
