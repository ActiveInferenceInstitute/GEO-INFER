"""
Integration tests for GEO-INFER-MARINE: marine ecosystem modeling pipeline.

Tests MarineEcosystemModeler through coral reef health, biodiversity, species
distribution, MPA effectiveness, climate impacts, and blue carbon estimation.
"""

import pytest
import numpy as np

try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False

pytestmark = [
    pytest.mark.integration,
]


@pytest.fixture
def sea_temperature():
    """Create synthetic sea surface temperature data (Celsius)."""
    np.random.seed(42)
    return xr.DataArray(
        np.random.uniform(22.0, 30.0, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(20.0, 25.0, 10),
            "lon": np.linspace(-88.0, -83.0, 10),
        },
    )


@pytest.fixture
def ocean_ph():
    """Create synthetic ocean pH data."""
    np.random.seed(43)
    return xr.DataArray(
        np.random.uniform(7.8, 8.3, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(20.0, 25.0, 10),
            "lon": np.linspace(-88.0, -83.0, 10),
        },
    )


@pytest.fixture
def bathymetry():
    """Create synthetic bathymetry/depth data (meters below sea level)."""
    np.random.seed(44)
    return xr.DataArray(
        np.random.uniform(5.0, 200.0, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(20.0, 25.0, 10),
            "lon": np.linspace(-88.0, -83.0, 10),
        },
    )


@pytest.fixture
def ecosystem_modeler():
    """Create a MarineEcosystemModeler instance."""
    from geo_infer_marine.core.marine_ecosystems import MarineEcosystemModeler
    return MarineEcosystemModeler()


class TestCoralReefAssessment:
    """Test coral reef health assessment pipeline."""

    def test_basic_coral_health(self, ecosystem_modeler, sea_temperature):
        """Test coral reef health from temperature alone."""
        result = ecosystem_modeler.assess_coral_reef_health(sea_temperature)

        assert "thermal_stress" in result
        assert "bleaching_risk" in result
        assert float(result["bleaching_risk"].min()) >= 0

    def test_coral_health_with_ph(self, ecosystem_modeler, sea_temperature, ocean_ph):
        """Test coral reef health with temperature and pH data."""
        result = ecosystem_modeler.assess_coral_reef_health(sea_temperature, ph=ocean_ph)

        assert "thermal_stress" in result
        assert "bleaching_risk" in result
        assert "acidification_stress" in result
        assert "combined_stress" in result


class TestBiodiversityAnalysis:
    """Test biodiversity index calculations."""

    def test_biodiversity_indices(self, ecosystem_modeler):
        """Test full biodiversity index calculation from species counts."""
        species_counts = {
            "parrotfish": 45,
            "clownfish": 30,
            "sea_turtle": 5,
            "barracuda": 15,
            "grouper": 20,
            "moray_eel": 8,
            "lionfish": 12,
        }

        result = ecosystem_modeler.calculate_biodiversity_indices(species_counts, area_km2=2.0)

        assert result["species_richness"] == 7
        assert result["total_abundance"] == 135
        assert 0 < result["shannon_diversity"] < 3
        assert 0 < result["simpson_diversity"] < 1
        assert 0 < result["evenness"] <= 1
        assert result["species_density"] == 3.5  # 7 species / 2 km^2

    def test_empty_species_returns_zeros(self, ecosystem_modeler):
        """Test empty species data returns all zero indices."""
        result = ecosystem_modeler.calculate_biodiversity_indices({})

        assert result["species_richness"] == 0
        assert result["shannon_diversity"] == 0
        assert result["simpson_diversity"] == 0

    def test_single_species_dominance(self, ecosystem_modeler):
        """Test biodiversity indices with single-species dominance."""
        species_counts = {"coral_trout": 100}
        result = ecosystem_modeler.calculate_biodiversity_indices(species_counts)

        assert result["species_richness"] == 1
        assert result["simpson_diversity"] == 0  # No diversity with one species


class TestSpeciesDistribution:
    """Test species distribution modeling pipeline."""

    def test_species_distribution_modeling(self, ecosystem_modeler, sea_temperature, bathymetry):
        """Test species distribution from environmental data."""
        from geo_infer_marine.core.marine_ecosystems import (
            SpeciesData, MarineHabitatType,
        )

        # Register a coral reef fish species
        species = SpeciesData(
            species_id="sp_001",
            common_name="Coral Trout",
            scientific_name="Plectropomus leopardus",
            trophic_level=4.0,
            habitat_preference=[MarineHabitatType.CORAL_REEF],
            temperature_range=(22.0, 29.0),
            depth_range=(5.0, 100.0),
            conservation_status="LC",
        )
        ecosystem_modeler.register_species(species)

        result = ecosystem_modeler.model_species_distribution(
            "sp_001", sea_temperature, bathymetry,
        )

        assert "suitability" in result
        assert "occurrence_probability" in result
        assert "temperature_suitability" in result
        assert "depth_suitability" in result

        # Probabilities should be in [0, 1]
        assert float(result["occurrence_probability"].min()) >= 0
        assert float(result["occurrence_probability"].max()) <= 1

    def test_unregistered_species_raises(self, ecosystem_modeler, sea_temperature, bathymetry):
        """Test that requesting an unregistered species raises ValueError."""
        with pytest.raises(ValueError, match="not registered"):
            ecosystem_modeler.model_species_distribution("nonexistent", sea_temperature, bathymetry)


class TestMarineProtectedAreas:
    """Test MPA creation and effectiveness assessment."""

    def test_create_and_assess_mpa(self, ecosystem_modeler):
        """Test creating an MPA and assessing its effectiveness."""
        # Create MPA
        mpa = ecosystem_modeler.create_marine_protected_area(
            mpa_id="mpa_001",
            name="Test Reef MPA",
            boundary=[
                (-86.0, 22.0), (-86.0, 23.0),
                (-85.0, 23.0), (-85.0, 22.0),
            ],
            protection_level="full",
            target_species=["sp_001"],
        )

        assert mpa["id"] == "mpa_001"
        assert mpa["area_km2"] > 0
        assert mpa["status"] == "active"

        # Assess effectiveness with more species inside than outside
        result = ecosystem_modeler.assess_mpa_effectiveness(
            "mpa_001",
            species_counts_inside={"parrotfish": 50, "grouper": 30, "turtle": 10},
            species_counts_outside={"parrotfish": 20, "grouper": 10},
            time_since_establishment_years=5.0,
        )

        assert result["mpa_name"] == "Test Reef MPA"
        assert result["abundance_ratio"] > 1.0, "Inside should be more abundant than outside"
        assert result["richness_ratio"] > 1.0, "Inside should have more species"
        assert 0 <= result["effectiveness_score"] <= 100
        assert "recommendation" in result


class TestClimateImpactAssessment:
    """Test climate change impact assessment."""

    def test_moderate_warming_scenario(self, ecosystem_modeler):
        """Test impact assessment under moderate warming."""
        result = ecosystem_modeler.assess_climate_change_impact(
            temperature_change=1.5,
            sea_level_rise_cm=30,
            ph_change=-0.15,
            time_horizon_years=50,
        )

        assert "coral_reef_impacts" in result
        assert "habitat_impacts" in result
        assert "species_impacts" in result
        assert "fisheries_impacts" in result
        assert 0 <= result["overall_vulnerability"] <= 1

        # Moderate warming should not cause extreme vulnerability
        assert result["adaptation_priority"] in ["moderate", "high", "critical"]

    def test_severe_warming_scenario(self, ecosystem_modeler):
        """Test impact assessment under severe warming."""
        result = ecosystem_modeler.assess_climate_change_impact(
            temperature_change=4.0,
            sea_level_rise_cm=100,
            ph_change=-0.4,
            time_horizon_years=100,
        )

        # Severe scenario should have high vulnerability
        assert result["overall_vulnerability"] > 0.5
        assert result["coral_reef_impacts"]["survival_probability"] < 0.5


class TestBlueCarbon:
    """Test blue carbon storage estimation."""

    def test_blue_carbon_estimation(self, ecosystem_modeler):
        """Test blue carbon storage across habitat types."""
        habitat_areas = {
            "mangrove": 50.0,
            "seagrass": 100.0,
            "salt_marsh": 30.0,
            "coral_reef": 200.0,
        }

        result = ecosystem_modeler.estimate_blue_carbon(habitat_areas, condition="healthy")

        assert result["total_area_km2"] == 380.0
        assert result["total_annual_storage_tonnes"] > 0
        assert result["condition_multiplier"] == 1.0
        assert result["carbon_value_usd_annual"] > 0
        assert result["carbon_value_usd_30yr"] == result["carbon_value_usd_annual"] * 30

        # Verify by-habitat breakdown
        assert "mangrove" in result["storage_by_habitat"]
        assert result["storage_by_habitat"]["mangrove"]["area_km2"] == 50.0

    def test_degraded_condition_reduces_storage(self, ecosystem_modeler):
        """Test that degraded habitat has lower carbon storage."""
        habitat_areas = {"mangrove": 50.0, "seagrass": 100.0}

        healthy = ecosystem_modeler.estimate_blue_carbon(habitat_areas, condition="healthy")
        degraded = ecosystem_modeler.estimate_blue_carbon(habitat_areas, condition="degraded")

        assert degraded["total_annual_storage_tonnes"] < healthy["total_annual_storage_tonnes"]
        assert degraded["condition_multiplier"] < healthy["condition_multiplier"]


class TestFisheriesModeling:
    """Test fisheries stock modeling."""

    def test_fisheries_stock_without_pressure(self, ecosystem_modeler):
        """Test stock modeling from habitat quality alone."""
        habitat = xr.DataArray(
            np.random.uniform(0.5, 1.0, (5, 5)),
            dims=["lat", "lon"],
        )

        result = ecosystem_modeler.model_fisheries_stock(habitat)
        assert "stock_abundance" in result
        assert float(result["stock_abundance"].min()) > 0

    def test_fishing_pressure_reduces_stock(self, ecosystem_modeler):
        """Test that fishing pressure reduces stock abundance."""
        habitat = xr.DataArray(np.full((5, 5), 0.8), dims=["lat", "lon"])
        pressure = xr.DataArray(np.full((5, 5), 30.0), dims=["lat", "lon"])

        no_pressure = ecosystem_modeler.model_fisheries_stock(habitat)
        with_pressure = ecosystem_modeler.model_fisheries_stock(habitat, fishing_pressure=pressure)

        assert float(with_pressure["stock_abundance"].mean()) < float(no_pressure["stock_abundance"].mean())
