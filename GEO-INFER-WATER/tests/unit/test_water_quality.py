"""Tests for water quality assessment module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-WATER/src")

from geo_infer_water.core.water_quality import (
    WaterQualityAssessor,
    WaterSample,
    WaterBodyType,
    PollutantType,
)


@pytest.fixture
def assessor():
    return WaterQualityAssessor()


@pytest.fixture
def good_sample():
    return WaterSample(
        sample_id="s001",
        location=(-73.0, 41.0),
        timestamp="2025-06-15",
        ph=7.2,
        dissolved_oxygen=8.5,
        turbidity=0.5,
        temperature=18.0,
        nitrate=2.0,
        e_coli=10,
    )


@pytest.fixture
def bad_sample():
    return WaterSample(
        sample_id="s002",
        location=(-73.0, 41.0),
        timestamp="2025-06-15",
        ph=5.0,
        dissolved_oxygen=2.0,
        turbidity=15.0,
        temperature=30.0,
        nitrate=25.0,
        e_coli=500,
    )


class TestWaterQualityAssessment:
    def test_compliant_ph(self, assessor):
        ph = xr.DataArray(np.full((5, 5), 7.0), dims=("y", "x"))
        result = assessor.assess_water_quality(ph)
        assert bool(result["ph_compliant"].all())

    def test_non_compliant_ph(self, assessor):
        ph = xr.DataArray(np.full((5, 5), 5.0), dims=("y", "x"))
        result = assessor.assess_water_quality(ph)
        assert not bool(result["ph_compliant"].any())


class TestWQI:
    def test_good_water_high_wqi(self, assessor, good_sample):
        result = assessor.calculate_wqi(good_sample)
        assert result["wqi"] > 50
        assert result["classification"] in ("Excellent", "Good")

    def test_bad_water_low_wqi(self, assessor, bad_sample):
        result = assessor.calculate_wqi(bad_sample)
        assert result["wqi"] < 50

    def test_wqi_returns_all_fields(self, assessor, good_sample):
        result = assessor.calculate_wqi(good_sample)
        assert "wqi" in result
        assert "classification" in result
        assert "sub_indices" in result


class TestPollutantLoad:
    def test_load_calculation(self, assessor):
        result = assessor.calculate_pollutant_load(
            concentration_mg_l=10.0,
            flow_rate_m3_s=1.0,
            time_period_hours=24.0,
        )
        assert result["load_kg"] > 0
        assert result["load_tonnes"] > 0
        assert result["load_kg"] == result["load_mg"] / 1e6


class TestRiskAssessment:
    def test_low_risk(self, assessor, good_sample):
        result = assessor.assess_risk(
            [good_sample], WaterBodyType.RIVER, usage_type="recreation"
        )
        assert result["risk_level"] in ("Low", "Moderate")

    def test_empty_samples(self, assessor):
        result = assessor.assess_risk([], WaterBodyType.LAKE)
        assert "error" in result


class TestRegulatoryCompliance:
    def test_compliant_water(self, assessor, good_sample):
        result = assessor.check_regulatory_compliance([good_sample])
        assert result["overall_compliant"] is True or result["compliance_rate"] > 0.5

    def test_different_regulations(self, assessor, good_sample):
        epa = assessor.check_regulatory_compliance([good_sample], "EPA")
        who = assessor.check_regulatory_compliance([good_sample], "WHO")
        assert "regulations" in epa
        assert epa["regulations"] == "EPA"
        assert who["regulations"] == "WHO"


class TestPollutionPlume:
    def test_plume_area_scales_with_diffusion(self, assessor):
        small = assessor.track_pollution_plume(
            initial_location=(-118.25, 34.05),
            pollutant_type=PollutantType.NUTRIENT,
            flow_velocity=(0.0, 0.0),
            diffusion_coefficient=1.0,
            time_hours=24,
        )
        large = assessor.track_pollution_plume(
            initial_location=(-118.25, 34.05),
            pollutant_type=PollutantType.NUTRIENT,
            flow_velocity=(0.0, 0.0),
            diffusion_coefficient=100.0,
            time_hours=24,
        )
        assert small["plume_area_km2"] > 0
        assert large["plume_area_km2"] > small["plume_area_km2"]

    def test_zero_diffusion_confines_to_source_cell(self, assessor):
        result = assessor.track_pollution_plume(
            initial_location=(-118.25, 34.05),
            pollutant_type=PollutantType.NUTRIENT,
            flow_velocity=(0.0, 0.0),
            diffusion_coefficient=0.0,
            time_hours=24,
        )
        field = np.asarray(result["concentration_field"])
        assert np.all(np.isfinite(field))
        assert result["dispersion_sigma_m"] == 0.0
        assert result["plume_area_km2"] > 0

    def test_advection_shifts_plume_center(self, assessor):
        result = assessor.track_pollution_plume(
            initial_location=(-118.25, 34.05),
            pollutant_type=PollutantType.ORGANIC,
            flow_velocity=(0.1, 0.0),
            diffusion_coefficient=10.0,
            time_hours=1.0,
        )
        lon, _ = result["plume_center"]
        assert lon > -118.25
