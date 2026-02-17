"""Tests for marine ecosystem modeling module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-MARINE/src")

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
