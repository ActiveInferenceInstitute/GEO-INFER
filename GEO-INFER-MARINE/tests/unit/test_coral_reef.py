"""Tests for coral reef health assessment module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-MARINE/src")

from geo_infer_marine.core.coral_reef import CoralReefAssessor


@pytest.fixture
def assessor():
    return CoralReefAssessor()


class TestDHW:
    def test_no_stress_below_mmm(self, assessor):
        sst = xr.DataArray(np.full(90, 26.0), dims=("time",))
        mmm = xr.DataArray(27.0)
        dhw = assessor.calculate_degree_heating_weeks(sst, mmm)
        assert float(dhw.max()) == 0.0

    def test_stress_above_threshold(self, assessor):
        sst = xr.DataArray(np.full(90, 29.0), dims=("time",))
        mmm = xr.DataArray(27.0)
        dhw = assessor.calculate_degree_heating_weeks(sst, mmm)
        assert float(dhw.max()) > 0

    def test_dhw_accumulates_over_time(self, assessor):
        sst = xr.DataArray(np.full(60, 29.0), dims=("time",))
        mmm = xr.DataArray(27.0)
        dhw = assessor.calculate_degree_heating_weeks(sst, mmm)
        assert float(dhw.isel(time=-1)) > float(dhw.isel(time=10))


class TestBleachingAlert:
    def test_no_stress_level_0(self, assessor):
        dhw = xr.DataArray(np.full((3,), 0.5), dims=("x",))
        alert = assessor.classify_bleaching_alert(dhw)
        assert int(alert.max()) == 0

    def test_level_1_watch(self, assessor):
        dhw = xr.DataArray(np.full((3,), 2.0), dims=("x",))
        alert = assessor.classify_bleaching_alert(dhw)
        assert int(alert.max()) == 1

    def test_level_4_alert(self, assessor):
        dhw = xr.DataArray(np.full((3,), 15.0), dims=("x",))
        alert = assessor.classify_bleaching_alert(dhw)
        assert int(alert.max()) == 4

    def test_progressive_levels(self, assessor):
        dhw = xr.DataArray(np.array([0.5, 2.0, 5.0, 9.0, 14.0]), dims=("x",))
        alert = assessor.classify_bleaching_alert(dhw)
        assert list(alert.values) == [0, 1, 2, 3, 4]


class TestReefBiodiversity:
    def test_empty_counts(self, assessor):
        result = assessor.calculate_reef_biodiversity({})
        assert result["species_richness"] == 0
        assert result["shannon_index"] == 0.0

    def test_single_species(self, assessor):
        result = assessor.calculate_reef_biodiversity({"coral_a": 100})
        assert result["species_richness"] == 1
        assert result["shannon_index"] < 0.01

    def test_diverse_community(self, assessor):
        counts = {f"species_{i}": 10 for i in range(20)}
        result = assessor.calculate_reef_biodiversity(counts)
        assert result["species_richness"] == 20
        assert result["shannon_index"] > 2.0
        assert result["evenness"] > 0.9

    def test_margalef_index(self, assessor):
        counts = {f"sp_{i}": 5 for i in range(10)}
        result = assessor.calculate_reef_biodiversity(counts)
        assert result["margalef_index"] > 0


class TestCompositeHealth:
    def test_healthy_reef(self, assessor):
        result = assessor.assess_reef_health_composite(
            coral_cover_pct=50.0,
            macroalgae_cover_pct=5.0,
            fish_biomass_kg_ha=1200.0,
            bleaching_alert_level=0,
        )
        assert result["classification"] == "healthy"
        assert result["composite_score"] > 75

    def test_degraded_reef(self, assessor):
        result = assessor.assess_reef_health_composite(
            coral_cover_pct=5.0,
            macroalgae_cover_pct=40.0,
            fish_biomass_kg_ha=100.0,
            bleaching_alert_level=3,
        )
        assert result["classification"] in ("degraded", "critical")
        assert result["composite_score"] < 50

    def test_thermal_penalty(self, assessor):
        result_0 = assessor.assess_reef_health_composite(30.0, 10.0, 800.0, 0)
        result_4 = assessor.assess_reef_health_composite(30.0, 10.0, 800.0, 4)
        assert result_0["composite_score"] > result_4["composite_score"]

    def test_score_range(self, assessor):
        result = assessor.assess_reef_health_composite(0.0, 100.0, 0.0, 4)
        assert result["composite_score"] >= 0
        assert result["composite_score"] <= 100
