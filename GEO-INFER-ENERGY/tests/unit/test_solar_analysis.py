"""Tests for solar analysis module."""

import numpy as np
import pytest

import sys
sys.path.insert(0, "GEO-INFER-ENERGY/src")

from geo_infer_energy.core.solar_analysis import SolarAnalyzer


@pytest.fixture
def analyzer():
    return SolarAnalyzer()


class TestSolarDeclination:
    def test_summer_solstice(self, analyzer):
        dec = analyzer.solar_declination(172)  # ~June 21
        assert dec > 20.0

    def test_winter_solstice(self, analyzer):
        dec = analyzer.solar_declination(355)  # ~Dec 21
        assert dec < -20.0

    def test_equinox(self, analyzer):
        dec = analyzer.solar_declination(80)  # ~March 21
        assert abs(dec) < 3.0


class TestSolarElevation:
    def test_noon_at_equator_equinox(self, analyzer):
        elev = analyzer.solar_elevation(0.0, 80, 12.0)
        assert elev > 85.0

    def test_midnight_below_horizon(self, analyzer):
        elev = analyzer.solar_elevation(45.0, 172, 0.0)
        assert elev < 0

    def test_polar_night(self, analyzer):
        elev = analyzer.solar_elevation(70.0, 355, 12.0)
        assert elev < 5.0


class TestClearSkyGHI:
    def test_positive_during_day(self, analyzer):
        ghi = analyzer.clear_sky_ghi(35.0, 172, 12.0)
        assert ghi > 500  # Strong midday sun

    def test_zero_at_night(self, analyzer):
        ghi = analyzer.clear_sky_ghi(35.0, 172, 0.0)
        assert ghi == 0.0

    def test_altitude_increases_irradiance(self, analyzer):
        ghi_sea = analyzer.clear_sky_ghi(35.0, 172, 12.0, 0.0)
        ghi_mountain = analyzer.clear_sky_ghi(35.0, 172, 12.0, 3000.0)
        assert ghi_mountain >= ghi_sea


class TestDailyInsolation:
    def test_summer_higher_than_winter(self, analyzer):
        summer = analyzer.daily_insolation(45.0, 172)
        winter = analyzer.daily_insolation(45.0, 355)
        assert summer > winter

    def test_positive_value(self, analyzer):
        insolation = analyzer.daily_insolation(35.0, 172)
        assert insolation > 0


class TestOptimalTilt:
    def test_tilt_positive(self, analyzer):
        tilt = analyzer.optimal_tilt_angle(45.0)
        assert tilt > 0

    def test_tilt_increases_with_latitude(self, analyzer):
        tilt_20 = analyzer.optimal_tilt_angle(20.0)
        tilt_50 = analyzer.optimal_tilt_angle(50.0)
        assert tilt_50 > tilt_20


class TestPVOutput:
    def test_basic_estimation(self, analyzer):
        result = analyzer.estimate_pv_output(
            ghi_kwh_m2_day=5.0,
            panel_area_m2=100.0,
            efficiency=0.20,
        )
        assert result["daily_kwh"] > 0
        assert result["annual_kwh"] > result["daily_kwh"]
        assert result["capacity_factor"] > 0
        assert result["capacity_factor"] < 1.0

    def test_zero_irradiance(self, analyzer):
        result = analyzer.estimate_pv_output(
            ghi_kwh_m2_day=0.0,
            panel_area_m2=100.0,
        )
        assert result["daily_kwh"] == 0.0


class TestTiltedIrradiance:
    def test_south_facing_optimal(self, analyzer):
        factor = analyzer.tilted_irradiance_factor(30.0, 180.0, 60.0, 180.0)
        assert factor > 0

    def test_below_horizon_zero(self, analyzer):
        factor = analyzer.tilted_irradiance_factor(30.0, 180.0, -5.0, 180.0)
        assert factor == 0.0
