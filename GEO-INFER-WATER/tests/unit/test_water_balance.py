"""Tests for water balance modeling module."""

import numpy as np
import pytest


from geo_infer_water.core.water_balance import WaterBalanceModeler


@pytest.fixture
def modeler():
    return WaterBalanceModeler()


class TestThornthwaitePET:
    def test_pet_positive_warm_months(self, modeler):
        temps = np.array([0, 2, 8, 14, 20, 24, 27, 26, 21, 14, 7, 2], dtype=float)
        pet = modeler.thornthwaite_pet(temps, latitude_deg=40.0)
        assert np.all(pet >= 0)
        assert float(np.max(pet)) > 0

    def test_pet_zero_cold_months(self, modeler):
        temps = np.full(12, -5.0)
        pet = modeler.thornthwaite_pet(temps, latitude_deg=60.0)
        np.testing.assert_allclose(pet, 0.0)

    def test_summer_pet_higher_than_winter(self, modeler):
        temps = np.array([0, 2, 8, 14, 20, 24, 27, 26, 21, 14, 7, 2], dtype=float)
        pet = modeler.thornthwaite_pet(temps, latitude_deg=40.0)
        summer_pet = np.mean(pet[5:8])
        winter_pet = np.mean(pet[0:3])
        assert summer_pet > winter_pet


class TestHargreavesPET:
    def test_positive_values(self, modeler):
        n = 30
        t_mean = np.full(n, 25.0)
        t_min = np.full(n, 18.0)
        t_max = np.full(n, 32.0)
        doy = np.arange(150, 150 + n)
        pet = modeler.hargreaves_pet(t_mean, t_min, t_max, 35.0, doy)
        assert np.all(pet >= 0)

    def test_higher_temp_higher_pet(self, modeler):
        doy = np.arange(170, 200)
        n = len(doy)
        pet_cool = modeler.hargreaves_pet(
            np.full(n, 15.0), np.full(n, 10.0), np.full(n, 20.0), 40.0, doy
        )
        pet_warm = modeler.hargreaves_pet(
            np.full(n, 30.0), np.full(n, 25.0), np.full(n, 35.0), 40.0, doy
        )
        assert float(np.mean(pet_warm)) > float(np.mean(pet_cool))


class TestSCSCurveNumber:
    def test_high_cn_more_runoff(self, modeler):
        precip = np.array([50.0, 100.0])
        runoff_90 = modeler.scs_curve_number_runoff(precip, curve_number=90)
        runoff_60 = modeler.scs_curve_number_runoff(precip, curve_number=60)
        assert float(np.sum(runoff_90)) > float(np.sum(runoff_60))

    def test_no_runoff_small_rain(self, modeler):
        precip = np.array([1.0])
        runoff = modeler.scs_curve_number_runoff(precip, curve_number=50)
        assert float(runoff[0]) == 0.0

    def test_runoff_less_than_precip(self, modeler):
        precip = np.array([80.0])
        runoff = modeler.scs_curve_number_runoff(precip, curve_number=85)
        assert float(runoff[0]) < 80.0
        assert float(runoff[0]) > 0

    def test_zero_cn(self, modeler):
        precip = np.array([50.0])
        runoff = modeler.scs_curve_number_runoff(precip, curve_number=0)
        np.testing.assert_allclose(runoff, 0.0)


class TestMonthlyWaterBalance:
    def test_balance_closure(self, modeler):
        precip = np.array([80, 70, 90, 100, 120, 60, 30, 20, 40, 70, 90, 80], dtype=float)
        pet = np.array([10, 15, 30, 50, 80, 100, 120, 110, 70, 40, 20, 10], dtype=float)
        result = modeler.monthly_water_balance(precip, pet)
        assert len(result["aet_mm"]) == 12
        assert np.all(result["aet_mm"] >= 0)
        assert np.all(result["surplus_mm"] >= 0)
        assert np.all(result["deficit_mm"] >= 0)

    def test_aet_does_not_exceed_pet(self, modeler):
        precip = np.full(12, 200.0)
        pet = np.full(12, 100.0)
        result = modeler.monthly_water_balance(precip, pet)
        assert np.all(result["aet_mm"] <= pet + 0.01)

    def test_storage_within_capacity(self, modeler):
        precip = np.full(12, 200.0)
        pet = np.full(12, 50.0)
        result = modeler.monthly_water_balance(precip, pet, soil_capacity_mm=150.0)
        assert np.all(result["soil_storage_mm"] <= 150.01)

    def test_drought_scenario(self, modeler):
        precip = np.full(12, 10.0)
        pet = np.full(12, 100.0)
        result = modeler.monthly_water_balance(precip, pet)
        assert np.sum(result["deficit_mm"]) > 0
        assert np.sum(result["surplus_mm"]) == 0
