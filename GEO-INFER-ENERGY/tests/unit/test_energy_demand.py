"""Tests for energy demand forecasting module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-ENERGY/src")

from geo_infer_energy.core.energy_demand import EnergyDemandForecaster


@pytest.fixture
def forecaster():
    return EnergyDemandForecaster()


class TestDemandForecast:
    def test_forecast_produces_output(self, forecaster):
        demand = xr.DataArray(
            np.linspace(100, 120, 10),
            dims=("time",),
            coords={"time": range(10)},
        )
        result = forecaster.forecast_demand(demand, forecast_years=5)
        assert "demand_forecast" in result


class TestPeakDemand:
    def test_identifies_peak(self, forecaster):
        values = np.array([50, 60, 100, 80, 55])
        demand = xr.DataArray(
            values,
            dims=("time",),
            coords={"time": range(5)},
        )
        result = forecaster.identify_peak_demand(demand)
        assert float(result["peak_demand"]) == 100.0
        assert float(result["peak_factor"]) > 1.0
