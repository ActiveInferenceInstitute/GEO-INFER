"""Tests for flood and drought analysis module."""

import numpy as np
import pytest
import xarray as xr


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

    def test_flood_risk_equal_weight_composite(self, analyzer):
        """Each indicator is averaged with equal weight (GS-160)."""
        # Constant precipitation is never strictly above its own 95th
        # percentile -> extreme-precip frequency 0; high elevation -> 0.
        precip = xr.DataArray(
            np.full(30, 5.0), dims=("time",), coords={"time": range(30)}
        )
        elevation = xr.DataArray(100.0)
        soil = xr.DataArray(1.0)
        result = analyzer.assess_flood_risk(precip, elevation, soil_saturation=soil)
        # sat-only hazard: (0 + 0 + 1) / 3, not the old 0.5
        assert float(result["flood_risk"].mean().values) == pytest.approx(1.0 / 3.0)
        # Without soil, two indicators: (0 + 0) / 2
        result2 = analyzer.assess_flood_risk(precip, elevation)
        assert float(result2["flood_risk"].mean().values) == pytest.approx(0.0)

    def test_drought_risk_equal_weight_composite(self, analyzer):
        """Drought indicators are averaged with equal weight (GS-160)."""
        # Constant precipitation is never strictly below its own 10th
        # percentile, and a constant soil-moisture field is never strictly
        # below its own 20th percentile -> all three indicators are 0.
        precip = xr.DataArray(
            np.full(30, 5.0), dims=("time",), coords={"time": range(30)}
        )
        soil = xr.DataArray(0.0)
        result = analyzer.assess_drought_risk(precip, soil_moisture=soil)
        assert float(result["drought_risk"].mean().values) == pytest.approx(0.0)


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

    def test_water_deficit_none_without_et(self, analyzer):
        precip = xr.DataArray(
            np.random.uniform(0, 10, (30, 5, 5)),
            dims=("time", "y", "x"),
            coords={"time": range(30)},
        )
        result = analyzer.assess_drought_risk(precip)
        # xarray stores the None sentinel as a scalar object variable.
        assert result["water_deficit"].shape == ()
        assert result["water_deficit"].values.item() is None

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
