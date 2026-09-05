"""Tests for fire risk assessment module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_forest.core.fire_risk import FireRiskAssessor


@pytest.fixture
def assessor():
    return FireRiskAssessor()


class TestKBDI:
    def test_kbdi_range(self, assessor):
        temps = np.full(30, 30.0)
        precip = np.zeros(30)
        kbdi = assessor.calculate_kbdi(temps, precip)
        assert np.all(kbdi >= 0)
        assert np.all(kbdi <= 800)

    def test_kbdi_increases_without_rain(self, assessor):
        temps = np.full(60, 35.0)
        precip = np.zeros(60)
        kbdi = assessor.calculate_kbdi(temps, precip)
        assert kbdi[-1] > kbdi[0]

    def test_kbdi_decreases_with_rain(self, assessor):
        temps = np.full(30, 30.0)
        precip = np.zeros(30)
        kbdi_dry = assessor.calculate_kbdi(temps, precip, initial_kbdi=500)
        precip_wet = np.full(30, 20.0)
        kbdi_wet = assessor.calculate_kbdi(temps, precip_wet, initial_kbdi=500)
        assert kbdi_wet[-1] < kbdi_dry[-1]

    def test_kbdi_starts_at_initial(self, assessor):
        temps = np.full(5, 20.0)
        precip = np.zeros(5)
        kbdi = assessor.calculate_kbdi(temps, precip, initial_kbdi=200)
        assert kbdi[0] == 200.0


class TestAngstromIndex:
    def test_high_danger(self, assessor):
        result = assessor.calculate_angstrom_index(40.0, 10.0)
        assert result["fire_danger"] == "high"
        assert result["angstrom_index"] < 2.0

    def test_low_danger(self, assessor):
        result = assessor.calculate_angstrom_index(10.0, 90.0)
        assert result["fire_danger"] in ("low", "very_low")
        assert result["angstrom_index"] > 2.5

    def test_moderate_conditions(self, assessor):
        result = assessor.calculate_angstrom_index(25.0, 40.0)
        assert "angstrom_index" in result
        assert "fire_danger" in result


class TestFuelMoisture:
    def test_dry_conditions(self, assessor):
        fm = assessor.calculate_fuel_moisture(35.0, 10.0)
        assert fm > 0
        assert fm < 10  # Very dry

    def test_wet_conditions(self, assessor):
        fm = assessor.calculate_fuel_moisture(15.0, 95.0)
        assert fm > 10

    def test_time_lag_effect(self, assessor):
        fm_1hr = assessor.calculate_fuel_moisture(30.0, 30.0, time_lag_hours=1.0)
        fm_100hr = assessor.calculate_fuel_moisture(30.0, 30.0, time_lag_hours=100.0)
        assert fm_100hr > fm_1hr

    def test_minimum_value(self, assessor):
        fm = assessor.calculate_fuel_moisture(50.0, 1.0)
        assert fm >= 1.0


class TestFireRiskGrid:
    def test_risk_range(self, assessor):
        temp = xr.DataArray(np.full((5, 5), 35.0), dims=("y", "x"))
        hum = xr.DataArray(np.full((5, 5), 15.0), dims=("y", "x"))
        wind = xr.DataArray(np.full((5, 5), 30.0), dims=("y", "x"))
        result = assessor.assess_fire_risk_grid(temp, hum, wind)
        assert float(result["fire_risk_index"].min()) >= 0
        assert float(result["fire_risk_index"].max()) <= 1

    def test_high_risk_conditions(self, assessor):
        temp = xr.DataArray(np.full((5, 5), 42.0), dims=("y", "x"))
        hum = xr.DataArray(np.full((5, 5), 5.0), dims=("y", "x"))
        wind = xr.DataArray(np.full((5, 5), 50.0), dims=("y", "x"))
        result = assessor.assess_fire_risk_grid(temp, hum, wind)
        assert float(result["fire_risk_index"].mean()) > 0.6

    def test_low_risk_conditions(self, assessor):
        temp = xr.DataArray(np.full((5, 5), 10.0), dims=("y", "x"))
        hum = xr.DataArray(np.full((5, 5), 90.0), dims=("y", "x"))
        wind = xr.DataArray(np.full((5, 5), 5.0), dims=("y", "x"))
        result = assessor.assess_fire_risk_grid(temp, hum, wind)
        assert float(result["fire_risk_index"].mean()) < 0.3

    def test_with_slope(self, assessor):
        temp = xr.DataArray(np.full((5, 5), 30.0), dims=("y", "x"))
        hum = xr.DataArray(np.full((5, 5), 30.0), dims=("y", "x"))
        wind = xr.DataArray(np.full((5, 5), 20.0), dims=("y", "x"))
        slope = xr.DataArray(np.full((5, 5), 30.0), dims=("y", "x"))
        result = assessor.assess_fire_risk_grid(temp, hum, wind, slope=slope)
        assert "fire_risk_index" in result
