"""Tests for coastal analysis module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_marine.core.coastal_analysis import CoastalAnalyzer


@pytest.fixture
def analyzer():
    return CoastalAnalyzer()


class TestCoastalVulnerability:
    def test_low_elevation_high_vulnerability(self, analyzer):
        elevation = xr.DataArray(np.full((5, 5), 1.0), dims=("y", "x"))
        sea_level = xr.DataArray(np.full((5, 5), 0.5), dims=("y", "x"))
        result = analyzer.assess_coastal_vulnerability(elevation, sea_level)
        assert "vulnerability_index" in result
        assert float(result["vulnerability_index"].mean()) > 0

    def test_high_elevation_low_vulnerability(self, analyzer):
        elevation = xr.DataArray(np.full((5, 5), 50.0), dims=("y", "x"))
        sea_level = xr.DataArray(np.full((5, 5), 0.5), dims=("y", "x"))
        result = analyzer.assess_coastal_vulnerability(elevation, sea_level)
        low_elev = xr.DataArray(np.full((5, 5), 2.0), dims=("y", "x"))
        result_low = analyzer.assess_coastal_vulnerability(low_elev, sea_level)
        assert float(result["vulnerability_index"].mean()) < float(
            result_low["vulnerability_index"].mean()
        )

    def test_wave_increases_vulnerability(self, analyzer):
        elevation = xr.DataArray(np.full((5, 5), 3.0), dims=("y", "x"))
        sea_level = xr.DataArray(np.full((5, 5), 0.5), dims=("y", "x"))
        wave = xr.DataArray(np.full((5, 5), 2.0), dims=("y", "x"))
        result_no_wave = analyzer.assess_coastal_vulnerability(elevation, sea_level)
        result_wave = analyzer.assess_coastal_vulnerability(elevation, sea_level, wave)
        assert float(result_wave["vulnerability_index"].mean()) > float(
            result_no_wave["vulnerability_index"].mean()
        )

    def test_below_sea_level_cells_bounded(self, analyzer):
        # relative_elevation == -1 previously caused division by zero
        # (inf); < -1 produced a negative, unbounded index.
        elevation = xr.DataArray([[-1.0, -5.0], [-0.5, 3.0]], dims=("y", "x"))
        sea_level = xr.DataArray(np.zeros((2, 2)), dims=("y", "x"))
        result = analyzer.assess_coastal_vulnerability(elevation, sea_level)
        vuln = result["vulnerability_index"].values
        assert np.isfinite(vuln).all()
        assert (vuln >= 0.0).all()
        assert (vuln <= 1.0).all()


class TestCoastalErosion:
    def test_erosion_calculation(self, analyzer):
        shoreline = xr.DataArray(
            np.array([[[100.0] * 5] * 5, [[95.0] * 5] * 5]),
            dims=("time", "y", "x"),
            coords={"time": [2020, 2025]},
        )
        result = analyzer.analyze_coastal_erosion(shoreline, [2020, 2025])
        assert "erosion_rates" in result
        assert float(result["erosion_rates"].mean()) > 0

    def test_single_time_period_raises_clear_error(self, analyzer):
        shoreline = xr.DataArray(np.full((1, 2, 2), 100.0), dims=("time", "y", "x"))
        with pytest.raises(ValueError, match="at least 2 time periods"):
            analyzer.analyze_coastal_erosion(shoreline, [2020])

    def test_no_time_periods_raises_clear_error(self, analyzer):
        shoreline = xr.DataArray(np.zeros((0, 2, 2)), dims=("time", "y", "x"))
        with pytest.raises(ValueError, match="at least 2 time periods"):
            analyzer.analyze_coastal_erosion(shoreline, [])
