"""Tests for marine spatial planning module."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_marine.core.marine_spatial_planning import MarineSpatialPlanner


@pytest.fixture
def planner():
    return MarineSpatialPlanner()


@pytest.fixture
def biodiversity_grid():
    grid = np.zeros((4, 4))
    grid[0, :] = 1.0
    grid[1, :] = 0.5
    return xr.DataArray(grid, dims=("lat", "lon"))


class TestDesignMpaNetwork:
    def test_meets_coverage_target(self, planner, biodiversity_grid):
        result = planner.design_mpa_network(biodiversity_grid, target_coverage=0.3)
        coverage = float(result["coverage"])
        assert coverage >= 0.3

    def test_higher_biodiversity_prioritized(self, planner, biodiversity_grid):
        result = planner.design_mpa_network(biodiversity_grid, target_coverage=0.25)
        priority = result["priority"].values
        # Top row (highest biodiversity) must have the highest priority.
        assert priority[0].min() >= priority[3].max()

    def test_all_zero_threat_data_yields_finite_priorities(self, planner, biodiversity_grid):
        threat = xr.zeros_like(biodiversity_grid)
        result = planner.design_mpa_network(biodiversity_grid, threat_data=threat)
        assert np.isfinite(result["priority"].values).all()

    def test_all_zero_biodiversity_yields_finite_priorities(self, planner):
        zero = xr.zeros_like(xr.DataArray(np.ones((4, 4)), dims=("lat", "lon")))
        result = planner.design_mpa_network(zero)
        priority = result["priority"].values
        assert np.isfinite(priority).all()
        assert (priority == 1.0).all()

    def test_all_zero_biodiversity_and_threat_stable(self, planner):
        zero = xr.zeros_like(xr.DataArray(np.ones((4, 4)), dims=("lat", "lon")))
        result = planner.design_mpa_network(zero, threat_data=zero)
        assert np.isfinite(result["priority"].values).all()


class TestOptimizeOffshoreWindSiting:
    def test_suitable_sites_scored_high(self, planner):
        wind = xr.DataArray(np.full((4, 4), 8.0), dims=("lat", "lon"))
        depth = xr.DataArray(np.full((4, 4), 10.0), dims=("lat", "lon"))
        result = planner.optimize_offshore_wind_siting(wind, depth)
        assert float(result["suitability"].max()) > 0.5

    def test_deep_water_excluded(self, planner):
        wind = xr.DataArray(np.full((2, 2), 8.0), dims=("lat", "lon"))
        depth = xr.DataArray([[10.0, 10.0], [100.0, 100.0]], dims=("lat", "lon"))
        result = planner.optimize_offshore_wind_siting(wind, depth, max_depth=50.0)
        assert float(result["suitability"].values[1, 0]) == pytest.approx(0.0)

    def test_exclusion_zones_zero_suitability(self, planner):
        wind = xr.DataArray(np.full((2, 2), 8.0), dims=("lat", "lon"))
        depth = xr.DataArray(np.full((2, 2), 10.0), dims=("lat", "lon"))
        exclusions = xr.DataArray(
            [[False, True], [False, False]], dims=("lat", "lon")
        )
        result = planner.optimize_offshore_wind_siting(wind, depth, exclusion_zones=exclusions)
        assert float(result["suitability"].values[0, 1]) == pytest.approx(0.0)

    def test_flat_wind_resource_no_nan(self, planner):
        wind = xr.zeros_like(xr.DataArray(np.ones((2, 2)), dims=("lat", "lon")))
        depth = xr.DataArray(np.full((2, 2), 10.0), dims=("lat", "lon"))
        result = planner.optimize_offshore_wind_siting(wind, depth)
        assert np.isfinite(result["suitability"].values).all()
