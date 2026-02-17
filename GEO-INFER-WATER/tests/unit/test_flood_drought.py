"""Tests for flood and drought analysis module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-WATER/src")

from geo_infer_water.core.flood_drought import FloodDroughtAnalyzer


@pytest.fixture
def analyzer():
    return FloodDroughtAnalyzer()


class TestFloodRisk:
    def test_flood_risk_output(self, analyzer):
        precip = xr.DataArray(
            np.random.uniform(0, 50, (30, 5, 5)),
            dims=("time", "y", "x"),
            coords={"time": range(30)},
        )
        elevation = xr.DataArray(
            np.random.uniform(0, 100, (5, 5)),
            dims=("y", "x"),
        )
        result = analyzer.assess_flood_risk(precip, elevation)
        assert "flood_risk" in result
        assert "extreme_precipitation" in result

    def test_flood_risk_range(self, analyzer):
        precip = xr.DataArray(
            np.random.uniform(0, 50, (30, 5, 5)),
            dims=("time", "y", "x"),
            coords={"time": range(30)},
        )
        elevation = xr.DataArray(
            np.random.uniform(0, 100, (5, 5)),
            dims=("y", "x"),
        )
        result = analyzer.assess_flood_risk(precip, elevation)
        assert float(result["flood_risk"].min()) >= 0
        assert float(result["flood_risk"].max()) <= 1


class TestDroughtRisk:
    def test_drought_risk_output(self, analyzer):
        precip = xr.DataArray(
            np.random.uniform(0, 10, (30, 5, 5)),
            dims=("time", "y", "x"),
            coords={"time": range(30)},
        )
        result = analyzer.assess_drought_risk(precip)
        assert "drought_risk" in result
        assert "low_precipitation" in result

    def test_with_evapotranspiration(self, analyzer):
        precip = xr.DataArray(
            np.random.uniform(0, 10, (30, 5, 5)),
            dims=("time", "y", "x"),
            coords={"time": range(30)},
        )
        et = xr.DataArray(
            np.random.uniform(5, 15, (30, 5, 5)),
            dims=("time", "y", "x"),
            coords={"time": range(30)},
        )
        result = analyzer.assess_drought_risk(precip, evapotranspiration=et)
        assert "drought_risk" in result
