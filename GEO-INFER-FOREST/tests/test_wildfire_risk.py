"""
Tests for the GEO-INFER-FOREST wildfire module.
"""

import pytest
import numpy as np
import xarray as xr

from geo_infer_forest.core.wildfire_risk import (
    WildfireRiskAnalyzer,
    FireDangerRating,
    FuelType,
    FireWeatherObservation,
    FireIncident
)


class TestWildfireRiskAnalyzer:
    """Test suite for WildfireRiskAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create an analyzer instance."""
        return WildfireRiskAnalyzer()
    
    def test_init(self, analyzer):
        """Test initialization."""
        assert analyzer.config == {}
        assert 'temperature_high' in analyzer.thresholds
        assert FuelType.GRASS in analyzer.base_spread_rates
    
    def test_assess_wildfire_risk(self, analyzer):
        """Test wildfire risk assessment."""
        temp = xr.DataArray([25, 30, 35], dims=['location'])
        precip = xr.DataArray(
            [[10, 5, 2], [8, 4, 1]],
            dims=['time', 'location']
        )
        
        result = analyzer.assess_wildfire_risk(temp, precip)
        
        assert 'wildfire_risk' in result
        assert 'drought_index' in result
        assert 'temperature_factor' in result
    
    def test_assess_with_fuel_load(self, analyzer):
        """Test risk assessment with fuel load."""
        temp = xr.DataArray([30, 35], dims=['location'])
        precip = xr.DataArray([[10, 5], [5, 2]], dims=['time', 'location'])
        fuel = xr.DataArray([80, 100], dims=['location'])
        
        result = analyzer.assess_wildfire_risk(temp, precip, fuel_load=fuel)
        
        assert 'wildfire_risk' in result


class TestFireWeatherIndex:
    """Test suite for FWI calculation."""
    
    @pytest.fixture
    def analyzer(self):
        return WildfireRiskAnalyzer()
    
    @pytest.fixture
    def low_risk_observation(self):
        return FireWeatherObservation(
            observation_id='FW_001',
            location=(-118.25, 34.05),
            timestamp='2024-01-15T14:00:00',
            temperature_c=20.0,
            relative_humidity=80.0,
            wind_speed_kmh=10.0,
            wind_direction_deg=180,
            precipitation_mm=5.0
        )
    
    @pytest.fixture
    def high_risk_observation(self):
        return FireWeatherObservation(
            observation_id='FW_002',
            location=(-118.25, 34.05),
            timestamp='2024-08-15T14:00:00',
            temperature_c=40.0,
            relative_humidity=10.0,
            wind_speed_kmh=50.0,
            wind_direction_deg=270,
            precipitation_mm=0.0
        )
    
    def test_calculate_fwi_low(self, analyzer, low_risk_observation):
        """Test FWI for low-risk conditions."""
        result = analyzer.calculate_fire_weather_index(low_risk_observation)
        
        assert 'fwi' in result
        assert 'components' in result
        assert result['danger_rating'] in ['low', 'moderate']
    
    def test_calculate_fwi_high(self, analyzer, high_risk_observation):
        """Test FWI for high-risk conditions."""
        result = analyzer.calculate_fire_weather_index(high_risk_observation)
        
        assert result['danger_rating'] in ['high', 'very_high', 'extreme']
    
    def test_fwi_components(self, analyzer, low_risk_observation):
        """Test FWI components are calculated."""
        result = analyzer.calculate_fire_weather_index(low_risk_observation)
        
        assert 'ffmc' in result['components']
        assert 'dmc' in result['components']
        assert 'dc' in result['components']
        assert 'isi' in result['components']
        assert 'bui' in result['components']


class TestFireSpreadModeling:
    """Test suite for fire spread modeling."""
    
    @pytest.fixture
    def analyzer(self):
        return WildfireRiskAnalyzer()
    
    def test_predict_fire_spread(self, analyzer):
        """Test fire spread prediction."""
        ignition = xr.DataArray([[0, 1, 0], [0, 0, 0]], dims=['y', 'x'])
        fuel = xr.DataArray([[50, 80, 60], [40, 70, 50]], dims=['y', 'x'])
        
        result = analyzer.predict_fire_spread(ignition, fuel)
        
        assert 'spread_probability' in result
        assert 'potential_spread' in result
    
    def test_model_fire_perimeter(self, analyzer):
        """Test fire perimeter modeling."""
        result = analyzer.model_fire_perimeter(
            ignition_point=(-118.25, 34.05),
            fuel_type=FuelType.GRASS,
            wind_speed_kmh=20.0,
            wind_direction_deg=270,
            slope_pct=10.0,
            time_hours=2.0
        )
        
        assert 'area_hectares' in result
        assert result['area_hectares'] > 0
        assert 'spread_rates' in result
        assert 'perimeter_x' in result
        assert 'perimeter_y' in result
    
    def test_perimeter_fuel_types(self, analyzer):
        """Test perimeter with different fuel types."""
        grass_result = analyzer.model_fire_perimeter(
            ignition_point=(-118.0, 34.0),
            fuel_type=FuelType.GRASS,
            wind_speed_kmh=15,
            wind_direction_deg=0,
            slope_pct=5,
            time_hours=1
        )
        
        timber_result = analyzer.model_fire_perimeter(
            ignition_point=(-118.0, 34.0),
            fuel_type=FuelType.TIMBER_LITTER,
            wind_speed_kmh=15,
            wind_direction_deg=0,
            slope_pct=5,
            time_hours=1
        )
        
        # Grass should spread faster than timber litter
        assert grass_result['area_hectares'] > timber_result['area_hectares']


class TestSuppressionPlanning:
    """Test suite for suppression resource planning."""
    
    @pytest.fixture
    def analyzer(self):
        return WildfireRiskAnalyzer()
    
    def test_plan_suppression_small_fire(self, analyzer):
        """Test suppression planning for small fire."""
        result = analyzer.plan_suppression_resources(
            fire_size_ha=10,
            danger_rating=FireDangerRating.MODERATE,
            terrain_difficulty='easy'
        )
        
        assert 'personnel' in result
        assert 'equipment' in result
        assert 'timeline' in result
        assert result['personnel']['firefighters_needed'] > 0
    
    def test_plan_suppression_large_fire(self, analyzer):
        """Test suppression planning for large fire."""
        result = analyzer.plan_suppression_resources(
            fire_size_ha=500,
            danger_rating=FireDangerRating.EXTREME,
            terrain_difficulty='difficult'
        )
        
        # Large extreme fire needs more resources
        assert result['personnel']['firefighters_needed'] > 100
        assert result['equipment']['helicopters'] >= 1
        assert result['equipment']['airtankers'] >= 1
    
    def test_suppression_terrain_factor(self, analyzer):
        """Test terrain affects resource needs."""
        easy = analyzer.plan_suppression_resources(
            fire_size_ha=100,
            danger_rating=FireDangerRating.HIGH,
            terrain_difficulty='easy'
        )
        
        difficult = analyzer.plan_suppression_resources(
            fire_size_ha=100,
            danger_rating=FireDangerRating.HIGH,
            terrain_difficulty='difficult'
        )
        
        assert difficult['personnel']['firefighters_needed'] > easy['personnel']['firefighters_needed']


class TestPostFireDamage:
    """Test suite for post-fire damage assessment."""
    
    @pytest.fixture
    def analyzer(self):
        return WildfireRiskAnalyzer()
    
    def test_assess_post_fire_damage(self, analyzer):
        """Test post-fire damage assessment."""
        pre_ndvi = xr.DataArray(
            [[0.7, 0.8, 0.75], [0.65, 0.7, 0.8]],
            dims=['y', 'x']
        )
        post_ndvi = xr.DataArray(
            [[0.2, 0.3, 0.6], [0.1, 0.5, 0.75]],
            dims=['y', 'x']
        )
        
        result = analyzer.assess_post_fire_damage(pre_ndvi, post_ndvi)
        
        assert 'dndvi' in result
        assert 'burn_severity' in result
        assert 'total_burned_pct' in result.attrs


class TestEvacuationZones:
    """Test suite for evacuation zone calculation."""
    
    @pytest.fixture
    def analyzer(self):
        return WildfireRiskAnalyzer()
    
    def test_calculate_evacuation_zones(self, analyzer):
        """Test evacuation zone calculation."""
        result = analyzer.calculate_evacuation_zones(
            fire_location=(-118.25, 34.05),
            predicted_spread_km=5.0,
            wind_direction_deg=270
        )
        
        assert 'zones' in result
        assert 'immediate_evacuation' in result['zones']
        assert 'evacuation_warning' in result['zones']
        assert 'evacuation_advisory' in result['zones']
    
    def test_zone_priorities(self, analyzer):
        """Test zone priorities are correct."""
        result = analyzer.calculate_evacuation_zones(
            fire_location=(-118.0, 34.0),
            predicted_spread_km=3.0,
            wind_direction_deg=180
        )
        
        zones = result['zones']
        assert zones['immediate_evacuation']['priority'] == 'CRITICAL'
        assert zones['evacuation_warning']['priority'] == 'HIGH'
        assert zones['evacuation_advisory']['priority'] == 'MODERATE'


class TestIncidentRegistry:
    """Test suite for incident registry."""
    
    @pytest.fixture
    def analyzer(self):
        return WildfireRiskAnalyzer()
    
    def test_register_incident(self, analyzer):
        """Test incident registration."""
        incident = FireIncident(
            incident_id='INC_001',
            name='Test Fire',
            location=(-118.25, 34.05),
            start_time='2024-08-15T10:00:00',
            area_hectares=50,
            containment_pct=10,
            cause='lightning'
        )
        
        result = analyzer.register_incident(incident)
        
        assert result == 'INC_001'
        assert len(analyzer.get_active_incidents()) == 1
    
    def test_get_active_incidents(self, analyzer):
        """Test getting active incidents."""
        for i in range(3):
            incident = FireIncident(
                incident_id=f'INC_{i}',
                name=f'Fire {i}',
                location=(-118.0, 34.0),
                start_time='2024-08-15',
                area_hectares=10 * (i + 1)
            )
            analyzer.register_incident(incident)
        
        incidents = analyzer.get_active_incidents()
        assert len(incidents) == 3


class TestEnums:
    """Test suite for enum types."""
    
    def test_fire_danger_ratings(self):
        """Test fire danger rating enum."""
        ratings = [
            FireDangerRating.LOW,
            FireDangerRating.MODERATE,
            FireDangerRating.HIGH,
            FireDangerRating.VERY_HIGH,
            FireDangerRating.EXTREME
        ]
        assert len(ratings) == 5
    
    def test_fuel_types(self):
        """Test fuel type enum."""
        types = [
            FuelType.GRASS,
            FuelType.SHRUB,
            FuelType.TIMBER_UNDERSTORY,
            FuelType.TIMBER_LITTER
        ]
        assert len(types) == 4


class TestAnisotropicSpread:
    """Wind direction must make spread faster downwind than upwind."""

    @pytest.fixture
    def analyzer(self):
        return WildfireRiskAnalyzer()

    @pytest.fixture
    def field(self):
        ignition = xr.DataArray([[0, 1, 0], [0, 0, 0]], dims=["y", "x"])
        fuel = xr.DataArray([[50.0, 80.0, 60.0], [40.0, 70.0, 50.0]], dims=["y", "x"])
        return ignition, fuel

    def test_downwind_faster_than_upwind(self, analyzer, field):
        ignition, fuel = field
        result = analyzer.predict_fire_spread(
            ignition, fuel, wind_direction=xr.DataArray(90.0)
        )
        downwind = float(result["directional_spread"].sel(direction=90.0).sum())
        upwind = float(result["directional_spread"].sel(direction=270.0).sum())
        assert downwind > upwind

    def test_multipliers_range(self, analyzer, field):
        """Multiplier floor is 1.0, ceiling is 1 + spread_boost."""
        ignition, fuel = field
        result = analyzer.predict_fire_spread(
            ignition, fuel, wind_direction=xr.DataArray(90.0), spread_boost=0.5
        )
        base = float(result["potential_spread"].sum())
        directional = result["directional_spread"].sum(dim=["y", "x"])
        ratios = directional / base
        assert float(ratios.min()) >= 1.0
        assert float(ratios.max()) <= 1.5 + 1e-9

    def test_isotropic_without_wind(self, analyzer, field):
        ignition, fuel = field
        result = analyzer.predict_fire_spread(ignition, fuel)
        assert float(result["directional_spread"].sel(direction=90.0).sum()) == (
            float(result["directional_spread"].sel(direction=270.0).sum())
        )
        assert "spread_probability" in result
        assert "potential_spread" in result

    def test_isotropic_equals_potential_spread(self, analyzer, field):
        """Without wind, directional_spread equals potential_spread in every direction."""
        ignition, fuel = field
        result = analyzer.predict_fire_spread(ignition, fuel)
        for direction in np.arange(0.0, 360.0, 45.0):
            np.testing.assert_allclose(
                result["directional_spread"].sel(direction=direction).values,
                result["potential_spread"].values,
            )
