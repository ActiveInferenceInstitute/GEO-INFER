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
