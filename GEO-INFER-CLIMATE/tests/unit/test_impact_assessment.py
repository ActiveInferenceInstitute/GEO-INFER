"""Tests for climate impact assessment module."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_climate.core.impact_assessment import ClimateImpactAssessor


@pytest.fixture
def assessor():
    return ClimateImpactAssessor()


class TestAgriculturalImpact:
    def test_optimal_conditions_zero_stress(self, assessor):
        temperature = xr.DataArray(20.0)
        precipitation = xr.DataArray(500.0)
        result = assessor.assess_agricultural_impact(temperature, precipitation, crop_type="wheat")
        assert float(result["combined_impact"]) == pytest.approx(0.0, abs=1e-9)

    def test_hot_dry_conditions_raise_impact(self, assessor):
        temperature = xr.DataArray(np.full(10, 35.0))
        precipitation = xr.DataArray(np.full(10, 100.0))
        result = assessor.assess_agricultural_impact(temperature, precipitation, crop_type="wheat")
        assert float(result["combined_impact"].mean()) > 0.5

    def test_unknown_crop_uses_default_optima(self, assessor):
        # Default optima are 22 deg C / 500 mm.
        result = assessor.assess_agricultural_impact(
            xr.DataArray(22.0), xr.DataArray(500.0), crop_type="quinoa"
        )
        assert float(result["combined_impact"]) == pytest.approx(0.0, abs=1e-9)

    def test_result_variables_present(self, assessor):
        result = assessor.assess_agricultural_impact(
            xr.DataArray(20.0), xr.DataArray(500.0)
        )
        for var in ("temperature_stress", "precipitation_stress", "combined_impact"):
            assert var in result


class TestWaterResources:
    def test_deficit_is_positive_when_dry(self, assessor):
        precipitation = xr.DataArray(10.0)
        et = xr.DataArray(50.0)
        result = assessor.assess_water_resources(precipitation, xr.DataArray(20.0), evapotranspiration=et)
        assert float(result["water_balance"]) == pytest.approx(-40.0)
        assert float(result["water_deficit"]) == pytest.approx(40.0)

    def test_no_deficit_when_wet(self, assessor):
        precipitation = xr.DataArray(80.0)
        et = xr.DataArray(50.0)
        result = assessor.assess_water_resources(precipitation, xr.DataArray(20.0), evapotranspiration=et)
        assert float(result["water_balance"]) == pytest.approx(30.0)
        assert float(result["water_deficit"]) == pytest.approx(0.0)

    def test_water_balance_sign_preserved(self, assessor):
        np.random.seed(42)
        precipitation = xr.DataArray(np.random.uniform(0.0, 100.0, 50))
        et = xr.DataArray(np.random.uniform(20.0, 60.0, 50))
        result = assessor.assess_water_resources(precipitation, xr.DataArray(20.0), evapotranspiration=et)
        balance = result["water_balance"].values
        deficit = result["water_deficit"].values
        assert np.all(deficit == np.where(balance < 0, -balance, 0))
