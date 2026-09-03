"""Tests for hydrology module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-WATER/src")

from geo_infer_water.core.hydrology import HydrologicalModeler


@pytest.fixture
def modeler():
    return HydrologicalModeler()


class TestRainfallRunoff:
    def test_runoff_and_infiltration_sum_to_precip(self, modeler):
        precip = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        result = modeler.rainfall_runoff_model(precip, infiltration_rate=0.6)
        total = result["runoff"] + result["infiltration"]
        np.testing.assert_allclose(total.values, 100.0, atol=1e-10)

    def test_zero_precipitation(self, modeler):
        precip = xr.DataArray(np.zeros((5, 5)), dims=("y", "x"))
        result = modeler.rainfall_runoff_model(precip)
        np.testing.assert_allclose(result["runoff"].values, 0.0)

    def test_soil_moisture_effect(self, modeler):
        precip = xr.DataArray(np.full((5, 5), 50.0), dims=("y", "x"))
        soil_dry = xr.DataArray(np.full((5, 5), 0.1), dims=("y", "x"))
        soil_wet = xr.DataArray(np.full((5, 5), 0.9), dims=("y", "x"))
        result_dry = modeler.rainfall_runoff_model(precip, soil_moisture=soil_dry)
        result_wet = modeler.rainfall_runoff_model(precip, soil_moisture=soil_wet)
        assert float(result_wet["runoff"].mean()) > float(result_dry["runoff"].mean())


class TestGroundwaterRecharge:
    def test_positive_recharge(self, modeler):
        infiltration = xr.DataArray(np.full((5, 5), 50.0), dims=("y", "x"))
        recharge = modeler.estimate_groundwater_recharge(infiltration)
        assert float(recharge.mean()) > 0

    def test_et_reduces_recharge(self, modeler):
        infiltration = xr.DataArray(np.full((5, 5), 50.0), dims=("y", "x"))
        et = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        recharge = modeler.estimate_groundwater_recharge(infiltration, et)
        assert float(recharge.mean()) < float(infiltration.mean())


class TestWaterBalance:
    def test_storage_change(self, modeler):
        precip = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        et = xr.DataArray(np.full((5, 5), 60.0), dims=("y", "x"))
        runoff = xr.DataArray(np.full((5, 5), 30.0), dims=("y", "x"))
        result = modeler.calculate_water_balance(precip, et, runoff)
        np.testing.assert_allclose(result["storage_change"].values, 10.0)
        # Closure: inflows - outflows - storage_change is exactly zero for
        # components constructed from the same terms.
        np.testing.assert_allclose(result["closure_residual"].values, 0.0)
        assert "balance" in result
