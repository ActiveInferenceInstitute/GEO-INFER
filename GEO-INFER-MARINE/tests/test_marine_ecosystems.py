"""
Tests for the GEO-INFER-MARINE ecosystems module.
"""

import pytest
import numpy as np
import xarray as xr

from geo_infer_MARINE.core.marine_ecosystems import (
    MarineEcosystemModeler,
    MarineHabitatType,
    SpeciesData
)


class TestMarineEcosystemModeler:
    """Test suite for MarineEcosystemModeler."""
    
    @pytest.fixture
    def modeler(self):
        """Create a modeler instance."""
        return MarineEcosystemModeler()
    
    def test_init(self, modeler):
        """Test initialization."""
        assert modeler.config == {}
        assert modeler.species_registry == {}
        assert modeler.mpa_registry == {}
    
    def test_assess_coral_reef_health(self, modeler):
        """Test coral reef health assessment."""
        temperature = xr.DataArray([24, 26, 28, 30], dims=['location'])
        
        result = modeler.assess_coral_reef_health(temperature)
        
        assert 'thermal_stress' in result
        assert 'bleaching_risk' in result
        assert len(result['bleaching_risk']) == 4
    
    def test_assess_coral_reef_health_with_ph(self, modeler):
        """Test coral reef health with pH."""
        temperature = xr.DataArray([26, 27], dims=['location'])
        ph = xr.DataArray([8.0, 7.8], dims=['location'])
        
        result = modeler.assess_coral_reef_health(temperature, ph)
        
        assert 'acidification_stress' in result
        assert 'combined_stress' in result
    
    def test_model_fisheries_stock(self, modeler):
        """Test fisheries stock modeling."""
        habitat = xr.DataArray([0.8, 0.6, 0.4], dims=['zone'])
        
        result = modeler.model_fisheries_stock(habitat)
        
        assert 'stock_abundance' in result
        assert float(result['stock_abundance'][0]) == 80.0
    
    def test_model_fisheries_with_pressure(self, modeler):
        """Test fisheries stock with fishing pressure."""
        habitat = xr.DataArray([0.8], dims=['zone'])
        pressure = xr.DataArray([50], dims=['zone'])  # 50% pressure
        
        result = modeler.model_fisheries_stock(habitat, pressure)
        
        assert float(result['stock_abundance'][0]) == 40.0  # Half due to pressure


class TestBiodiversityIndices:
    """Test suite for biodiversity calculations."""
    
    @pytest.fixture
    def modeler(self):
        return MarineEcosystemModeler()
    
    def test_calculate_biodiversity_empty(self, modeler):
        """Test biodiversity with empty data."""
        result = modeler.calculate_biodiversity_indices({})
        
        assert result['species_richness'] == 0
        assert result['shannon_diversity'] == 0
    
    def test_calculate_biodiversity_single_species(self, modeler):
        """Test biodiversity with single species."""
        result = modeler.calculate_biodiversity_indices({'sp1': 100})
        
        assert result['species_richness'] == 1
        assert result['total_abundance'] == 100
    
    def test_calculate_biodiversity_multiple_species(self, modeler):
        """Test biodiversity with multiple species."""
        species_counts = {
            'sp1': 50,
            'sp2': 30,
            'sp3': 20
        }
        
        result = modeler.calculate_biodiversity_indices(species_counts)
        
        assert result['species_richness'] == 3
        assert result['total_abundance'] == 100
        assert result['shannon_diversity'] > 0
        assert 0 <= result['simpson_diversity'] <= 1
        assert 0 <= result['evenness'] <= 1
    
    def test_species_density(self, modeler):
        """Test species density calculation."""
        species_counts = {'sp1': 10, 'sp2': 20, 'sp3': 30, 'sp4': 40}
        
        result = modeler.calculate_biodiversity_indices(species_counts, area_km2=2.0)
        
        assert result['species_density'] == 2.0  # 4 species / 2 km²


class TestSpeciesDistribution:
    """Test suite for species distribution modeling."""
    
    @pytest.fixture
    def modeler(self):
        modeler = MarineEcosystemModeler()
        
        # Register a test species
        species = SpeciesData(
            species_id='clownfish_001',
            common_name='Clownfish',
            scientific_name='Amphiprion ocellaris',
            trophic_level=3.0,
            habitat_preference=[MarineHabitatType.CORAL_REEF],
            temperature_range=(24.0, 30.0),
            depth_range=(1.0, 15.0),
            conservation_status="LC"
        )
        modeler.register_species(species)
        
        return modeler
    
    def test_register_species(self, modeler):
        """Test species registration."""
        assert 'clownfish_001' in modeler.species_registry
        species = modeler.species_registry['clownfish_001']
        assert species.common_name == 'Clownfish'
    
    def test_model_species_distribution(self, modeler):
        """Test species distribution modeling."""
        temperature = xr.DataArray([26, 27, 32, 20], dims=['location'])
        depth = xr.DataArray([5, 10, 25, 5], dims=['location'])
        
        result = modeler.model_species_distribution('clownfish_001', temperature, depth)
        
        assert 'suitability' in result
        assert 'occurrence_probability' in result
        # Optimal conditions should have higher suitability
        assert float(result['suitability'][0]) > float(result['suitability'][2])
    
    def test_species_not_found(self, modeler):
        """Test error for unregistered species."""
        temperature = xr.DataArray([26], dims=['location'])
        depth = xr.DataArray([10], dims=['location'])
        
        with pytest.raises(ValueError, match="not registered"):
            modeler.model_species_distribution('unknown', temperature, depth)


class TestMarineProtectedAreas:
    """Test suite for MPA functionality."""
    
    @pytest.fixture
    def modeler(self):
        return MarineEcosystemModeler()
    
    def test_create_mpa(self, modeler):
        """Test MPA creation."""
        boundary = [
            (-118.5, 33.5),
            (-118.0, 33.5),
            (-118.0, 34.0),
            (-118.5, 34.0)
        ]
        
        mpa = modeler.create_marine_protected_area(
            mpa_id='MPA_001',
            name='Test Marine Reserve',
            boundary=boundary,
            protection_level='full'
        )
        
        assert mpa['id'] == 'MPA_001'
        assert mpa['name'] == 'Test Marine Reserve'
        assert mpa['protection_level'] == 'full'
        assert mpa['area_km2'] > 0
    
    def test_assess_mpa_effectiveness(self, modeler):
        """Test MPA effectiveness assessment."""
        # Create an MPA
        boundary = [(-118.5, 33.5), (-118.0, 33.5), (-118.0, 34.0), (-118.5, 34.0)]
        modeler.create_marine_protected_area(
            mpa_id='MPA_001',
            name='Test MPA',
            boundary=boundary
        )
        
        # Assess effectiveness
        inside = {'sp1': 100, 'sp2': 80, 'sp3': 60}
        outside = {'sp1': 50, 'sp2': 40, 'sp3': 30}
        
        result = modeler.assess_mpa_effectiveness(
            mpa_id='MPA_001',
            species_counts_inside=inside,
            species_counts_outside=outside,
            time_since_establishment_years=5.0
        )
        
        assert result['abundance_ratio'] == 2.0  # Inside has 2x abundance
        assert result['richness_ratio'] == 1.0  # Same number of species
        assert 'effectiveness_score' in result
        assert 'recommendation' in result
    
    def test_mpa_not_found(self, modeler):
        """Test error for unknown MPA."""
        with pytest.raises(ValueError, match="not found"):
            modeler.assess_mpa_effectiveness(
                mpa_id='UNKNOWN',
                species_counts_inside={'sp1': 10},
                species_counts_outside={'sp1': 5}
            )


class TestClimateImpact:
    """Test suite for climate change impact assessment."""
    
    @pytest.fixture
    def modeler(self):
        return MarineEcosystemModeler()
    
    def test_assess_climate_impact(self, modeler):
        """Test climate impact assessment."""
        result = modeler.assess_climate_change_impact(
            temperature_change=2.0,
            sea_level_rise_cm=50,
            ph_change=-0.2,
            time_horizon_years=50
        )
        
        assert 'coral_reef_impacts' in result
        assert 'habitat_impacts' in result
        assert 'species_impacts' in result
        assert 'fisheries_impacts' in result
        assert 0 <= result['overall_vulnerability'] <= 1
    
    def test_climate_impact_severity(self, modeler):
        """Test that higher changes result in higher vulnerability."""
        mild = modeler.assess_climate_change_impact(
            temperature_change=0.5,
            sea_level_rise_cm=10,
            ph_change=-0.05
        )
        
        severe = modeler.assess_climate_change_impact(
            temperature_change=3.0,
            sea_level_rise_cm=100,
            ph_change=-0.4
        )
        
        assert severe['overall_vulnerability'] > mild['overall_vulnerability']


class TestBlueCarbon:
    """Test suite for blue carbon estimation."""
    
    @pytest.fixture
    def modeler(self):
        return MarineEcosystemModeler()
    
    def test_estimate_blue_carbon(self, modeler):
        """Test blue carbon estimation."""
        habitat_areas = {
            'mangrove': 100,
            'seagrass': 200,
            'salt_marsh': 50
        }
        
        result = modeler.estimate_blue_carbon(habitat_areas, condition='healthy')
        
        assert result['total_area_km2'] == 350
        assert result['total_annual_storage_tonnes'] > 0
        assert result['condition_multiplier'] == 1.0
        assert result['carbon_value_usd_annual'] > 0
    
    def test_blue_carbon_degraded(self, modeler):
        """Test blue carbon with degraded condition."""
        habitat_areas = {'mangrove': 100}
        
        healthy = modeler.estimate_blue_carbon(habitat_areas, condition='healthy')
        degraded = modeler.estimate_blue_carbon(habitat_areas, condition='degraded')
        
        # Degraded should have lower storage
        assert degraded['total_annual_storage_tonnes'] < healthy['total_annual_storage_tonnes']
        assert degraded['condition_multiplier'] == 0.6


class TestHabitatTypes:
    """Test suite for habitat type enums."""
    
    def test_habitat_types_exist(self):
        """Test all habitat types."""
        types = [
            MarineHabitatType.CORAL_REEF,
            MarineHabitatType.SEAGRASS,
            MarineHabitatType.MANGROVE,
            MarineHabitatType.KELP_FOREST,
            MarineHabitatType.OPEN_OCEAN,
            MarineHabitatType.DEEP_SEA,
            MarineHabitatType.ESTUARY
        ]
        
        assert len(types) == 7
    
    def test_habitat_type_values(self):
        """Test habitat type values."""
        assert MarineHabitatType.CORAL_REEF.value == "coral_reef"
        assert MarineHabitatType.SEAGRASS.value == "seagrass"
