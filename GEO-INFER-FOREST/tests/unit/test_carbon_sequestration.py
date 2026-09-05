"""Tests for carbon sequestration module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_forest.core.carbon_sequestration import CarbonSequestrationModeler


@pytest.fixture
def modeler():
    return CarbonSequestrationModeler()


class TestCarbonStock:
    def test_carbon_is_fraction_of_biomass(self, modeler):
        biomass = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        carbon = modeler.calculate_carbon_stock(biomass)
        np.testing.assert_allclose(carbon.values, 50.0)

    def test_zero_biomass(self, modeler):
        biomass = xr.DataArray(np.zeros((5, 5)), dims=("y", "x"))
        carbon = modeler.calculate_carbon_stock(biomass)
        np.testing.assert_allclose(carbon.values, 0.0)


class TestSequestrationRate:
    def test_rate_calculation(self, modeler):
        growth = xr.DataArray(np.full((5, 5), 5.0), dims=("y", "x"))
        rate = modeler.estimate_sequestration_rate(growth)
        np.testing.assert_allclose(rate.values, 2.5)

    def test_multi_year_period(self, modeler):
        growth = xr.DataArray(np.full((5, 5), 10.0), dims=("y", "x"))
        rate = modeler.estimate_sequestration_rate(growth, time_period=2.0)
        np.testing.assert_allclose(rate.values, 2.5)


class TestCarbonCredits:
    def test_credit_value(self, modeler):
        seq = xr.DataArray(np.full((3, 3), 1.0), dims=("y", "x"))
        area = xr.DataArray(np.full((3, 3), 10.0), dims=("y", "x"))
        credits = modeler.calculate_carbon_credits(seq, area, price_per_ton=50.0)
        expected = 1.0 * 3.67 * 10.0 * 50.0
        np.testing.assert_allclose(credits.values, expected, rtol=1e-5)

    def test_zero_area(self, modeler):
        seq = xr.DataArray(np.full((3, 3), 5.0), dims=("y", "x"))
        area = xr.DataArray(np.zeros((3, 3)), dims=("y", "x"))
        credits = modeler.calculate_carbon_credits(seq, area)
        np.testing.assert_allclose(credits.values, 0.0)
