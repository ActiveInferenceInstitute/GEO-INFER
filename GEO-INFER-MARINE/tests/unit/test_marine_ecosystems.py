"""Tests for marine ecosystem modeling module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_marine.core.marine_ecosystems import (
    MarineEcosystemModeler,
    MarineHabitatType,
    SpeciesData,
)


@pytest.fixture
def modeler():
    return MarineEcosystemModeler()


class TestBiodiversityIndices:
    def test_empty_community(self, modeler):
        result = modeler.calculate_biodiversity_indices({})
        assert result["species_richness"] == 0
        assert result["shannon_diversity"] == 0

    def test_even_community(self, modeler):
        counts = {"sp_a": 50, "sp_b": 50, "sp_c": 50, "sp_d": 50}
        result = modeler.calculate_biodiversity_indices(counts)
        assert result["species_richness"] == 4
        assert result["evenness"] > 0.95

    def test_uneven_community(self, modeler):
        counts = {"dominant": 990, "rare_1": 5, "rare_2": 3, "rare_3": 2}
        result = modeler.calculate_biodiversity_indices(counts)
        assert result["evenness"] < 0.5


class TestCoralReefHealth:
    def test_optimal_temperature(self, modeler):
        temp = xr.DataArray(np.full((5, 5), 26.0), dims=("y", "x"))
        result = modeler.assess_coral_reef_health(temp)
        assert float(result["thermal_stress"].mean()) < 1.0

    def test_high_temperature_stress(self, modeler):
        temp = xr.DataArray(np.full((5, 5), 32.0), dims=("y", "x"))
        result = modeler.assess_coral_reef_health(temp)
        assert float(result["bleaching_risk"].mean()) > 0.5

    def test_with_ph(self, modeler):
        temp = xr.DataArray(np.full((5, 5), 27.0), dims=("y", "x"))
        ph = xr.DataArray(np.full((5, 5), 7.8), dims=("y", "x"))
        result = modeler.assess_coral_reef_health(temp, ph=ph)
        assert "acidification_stress" in result


class TestSpeciesDistribution:
    def test_model_species(self, modeler):
        species = SpeciesData(
            species_id="clownfish",
            common_name="Clownfish",
            scientific_name="Amphiprion ocellaris",
            trophic_level=3.0,
            habitat_preference=[MarineHabitatType.CORAL_REEF],
            temperature_range=(24.0, 30.0),
            depth_range=(1.0, 15.0),
        )
        modeler.register_species(species)

        temp = xr.DataArray(np.full((5, 5), 27.0), dims=("y", "x"))
        depth = xr.DataArray(np.full((5, 5), 8.0), dims=("y", "x"))
        result = modeler.model_species_distribution("clownfish", temp, depth)
        assert float(result["suitability"].max()) > 0.5

    def test_unregistered_species(self, modeler):
        temp = xr.DataArray(np.full((3, 3), 20.0), dims=("y", "x"))
        depth = xr.DataArray(np.full((3, 3), 50.0), dims=("y", "x"))
        with pytest.raises(ValueError, match="not registered"):
            modeler.model_species_distribution("unknown", temp, depth)


class TestBlueCarbon:
    def test_storage_calculation(self, modeler):
        habitats = {"mangrove": 10.0, "seagrass": 5.0}
        result = modeler.estimate_blue_carbon(habitats)
        assert result["total_annual_storage_tonnes"] > 0
        assert result["carbon_value_usd_annual"] > 0

    def test_degraded_condition(self, modeler):
        habitats = {"mangrove": 10.0}
        healthy = modeler.estimate_blue_carbon(habitats, condition="healthy")
        degraded = modeler.estimate_blue_carbon(habitats, condition="degraded")
        assert healthy["total_annual_storage_tonnes"] > degraded["total_annual_storage_tonnes"]


class TestBiodiversityEdgeCases:
    def test_single_species(self, modeler):
        result = modeler.calculate_biodiversity_indices({"sp1": 100})
        assert result["species_richness"] == 1
        assert result["total_abundance"] == 100
        assert result["simpson_diversity"] == pytest.approx(0.0)

    def test_species_density(self, modeler):
        counts = {"sp1": 10, "sp2": 20, "sp3": 30, "sp4": 40}
        result = modeler.calculate_biodiversity_indices(counts, area_km2=2.0)
        assert result["species_density"] == pytest.approx(2.0)


class TestFisheriesStock:
    def test_model_stock(self, modeler):
        quality = xr.DataArray([1.0, 0.5], dims="site")
        result = modeler.model_fisheries_stock(habitat_quality=quality)
        assert float(result["stock_abundance"][0]) == pytest.approx(100.0)
        assert float(result["stock_abundance"][1]) == pytest.approx(50.0)

    def test_stock_with_fishing_pressure(self, modeler):
        quality = xr.DataArray([1.0], dims="site")
        pressure = xr.DataArray([60.0], dims="site")
        result = modeler.model_fisheries_stock(
            habitat_quality=quality, fishing_pressure=pressure
        )
        assert float(result["stock_abundance"][0]) == pytest.approx(40.0)


class TestMarineProtectedAreas:
    def test_create_mpa(self, modeler):
        boundary = [
            (-118.5, 33.5),
            (-118.0, 33.5),
            (-118.0, 34.0),
            (-118.5, 34.0),
        ]
        mpa = modeler.create_marine_protected_area(
            mpa_id="MPA_001",
            name="Test Marine Reserve",
            boundary=boundary,
            protection_level="full",
        )
        assert mpa["id"] == "MPA_001"
        assert mpa["protection_level"] == "full"
        assert mpa["area_km2"] > 0

    def test_assess_mpa_effectiveness(self, modeler):
        boundary = [(-118.5, 33.5), (-118.0, 33.5), (-118.0, 34.0), (-118.5, 34.0)]
        modeler.create_marine_protected_area(
            mpa_id="MPA_001", name="Test MPA", boundary=boundary
        )
        result = modeler.assess_mpa_effectiveness(
            mpa_id="MPA_001",
            species_counts_inside={"sp1": 100, "sp2": 80, "sp3": 60},
            species_counts_outside={"sp1": 50, "sp2": 40, "sp3": 30},
            time_since_establishment_years=5.0,
        )
        assert result["abundance_ratio"] == pytest.approx(2.0)
        assert result["richness_ratio"] == pytest.approx(1.0)
        assert "effectiveness_score" in result

    def test_mpa_not_found(self, modeler):
        with pytest.raises(ValueError, match="not found"):
            modeler.assess_mpa_effectiveness(
                mpa_id="UNKNOWN",
                species_counts_inside={"sp1": 10},
                species_counts_outside={"sp1": 5},
            )


class TestClimateImpact:
    def test_impact_structure(self, modeler):
        result = modeler.assess_climate_change_impact(
            temperature_change=2.0,
            sea_level_rise_cm=50,
            ph_change=-0.2,
            time_horizon_years=50,
        )
        assert "coral_reef_impacts" in result
        assert 0 <= result["overall_vulnerability"] <= 1

    def test_severity_ordering(self, modeler):
        mild = modeler.assess_climate_change_impact(
            temperature_change=0.5, sea_level_rise_cm=10, ph_change=-0.05
        )
        severe = modeler.assess_climate_change_impact(
            temperature_change=3.0, sea_level_rise_cm=100, ph_change=-0.4
        )
        assert severe["overall_vulnerability"] > mild["overall_vulnerability"]
