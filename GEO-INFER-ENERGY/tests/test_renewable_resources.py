"""
Tests for the GEO-INFER-ENERGY renewable resources module.
"""

import pytest
import numpy as np
import xarray as xr

from geo_infer_energy.core.renewable_resources import (
    RenewableResourceAssessor,
    RenewableType,
    SuitabilityClass,
    RenewableSite
)


class TestRenewableResourceAssessor:
    """Test suite for RenewableResourceAssessor."""
    
    @pytest.fixture
    def assessor(self):
        """Create an assessor instance."""
        return RenewableResourceAssessor()
    
    def test_init(self, assessor):
        """Test initialization."""
        assert assessor.config == {}
        assert RenewableType.SOLAR_PV in assessor.efficiency
        assert RenewableType.ONSHORE_WIND in assessor.capital_costs
    
    def test_assess_solar_potential(self, assessor):
        """Test solar potential assessment."""
        irradiance = xr.DataArray([5.0, 6.0, 7.0], dims=['location'])
        
        result = assessor.assess_solar_potential(irradiance)
        
        assert 'solar_potential' in result
        assert 'annual_energy' in result
    
    def test_assess_solar_with_terrain(self, assessor):
        """Test solar with terrain factors."""
        irradiance = xr.DataArray([5.0, 6.0], dims=['location'])
        slope = xr.DataArray([30.0, 60.0], dims=['location'])  # 30° is optimal
        aspect = xr.DataArray([180, 90], dims=['location'])  # South vs East
        
        result = assessor.assess_solar_potential(irradiance, slope=slope, aspect=aspect)
        
        # First location should have higher potential (optimal slope, south-facing)
        assert float(result['solar_potential'].values[0]) > float(result['solar_potential'].values[1])
    
    def test_assess_wind_potential(self, assessor):
        """Test wind potential assessment."""
        wind_speed = xr.DataArray([6, 8, 10], dims=['location'])
        
        result = assessor.assess_wind_potential(wind_speed)
        
        assert 'wind_power' in result
        assert 'energy_potential' in result
    
    def test_assess_hydro_potential(self, assessor):
        """Test hydro potential assessment."""
        flow = xr.DataArray([10, 20], dims=['location'])
        head = xr.DataArray([50, 100], dims=['location'])
        
        result = assessor.assess_hydro_potential(flow, head)
        
        assert 'hydro_power' in result
        assert float(result['hydro_power'].values[1]) > float(result['hydro_power'].values[0])


class TestSiteSuitability:
    """Test suite for site suitability assessment."""
    
    @pytest.fixture
    def assessor(self):
        return RenewableResourceAssessor()
    
    def test_assess_excellent_site(self, assessor):
        """Test excellent site suitability."""
        result = assessor.assess_site_suitability(
            location=(-118.25, 34.05),
            resource_type=RenewableType.SOLAR_PV,
            resource_value=7.0  # High irradiance
        )
        
        assert result['suitability_class'] == 'excellent'
        assert result['development_recommended'] == True
    
    def test_assess_poor_site(self, assessor):
        """Test poor site suitability."""
        result = assessor.assess_site_suitability(
            location=(-118.25, 34.05),
            resource_type=RenewableType.SOLAR_PV,
            resource_value=2.0  # Low irradiance
        )
        
        assert result['suitability_class'] in ['marginal', 'unsuitable']
    
    def test_constraints_affect_suitability(self, assessor):
        """Test constraints reduce suitability."""
        without_constraints = assessor.assess_site_suitability(
            location=(-118.0, 34.0),
            resource_type=RenewableType.ONSHORE_WIND,
            resource_value=8.0
        )
        
        with_constraints = assessor.assess_site_suitability(
            location=(-118.0, 34.0),
            resource_type=RenewableType.ONSHORE_WIND,
            resource_value=8.0,
            constraints={'poor_access': True, 'steep_slope': True}
        )
        
        assert with_constraints['final_score'] < without_constraints['final_score']
    
    def test_protected_area_blocks_development(self, assessor):
        """Test protected areas block development."""
        result = assessor.assess_site_suitability(
            location=(-118.0, 34.0),
            resource_type=RenewableType.SOLAR_PV,
            resource_value=7.0,
            constraints={'protected_area': True}
        )
        
        assert result['development_recommended'] == False
        assert result['final_score'] == 0


class TestCapacityFactor:
    """Test suite for capacity factor calculation."""
    
    @pytest.fixture
    def assessor(self):
        return RenewableResourceAssessor()
    
    def test_solar_capacity_factor(self, assessor):
        """Test solar capacity factor."""
        # Simulate daily irradiance pattern
        hours = np.arange(8760)
        irradiance = np.maximum(0, 500 * np.sin(2 * np.pi * (hours % 24) / 24 - np.pi/4))
        resource_data = xr.DataArray(irradiance, dims=['time'])
        
        result = assessor.calculate_capacity_factor(
            RenewableType.SOLAR_PV,
            resource_data,
            rated_capacity_mw=100
        )
        
        assert 'capacity_factor' in result
        assert 0 < result['capacity_factor'] < 0.5  # Solar typically 15-25%
    
    def test_wind_capacity_factor(self, assessor):
        """Test wind capacity factor."""
        # Simulate wind speeds
        wind_speeds = np.random.weibull(2, 8760) * 8  # Weibull distribution
        resource_data = xr.DataArray(wind_speeds, dims=['time'])
        
        result = assessor.calculate_capacity_factor(
            RenewableType.ONSHORE_WIND,
            resource_data,
            rated_capacity_mw=50
        )
        
        assert 'capacity_factor' in result
        assert 'annual_generation_gwh' in result


class TestLCOE:
    """Test suite for LCOE calculation."""
    
    @pytest.fixture
    def assessor(self):
        return RenewableResourceAssessor()
    
    def test_calculate_lcoe_solar(self, assessor):
        """Test LCOE calculation for solar."""
        result = assessor.calculate_lcoe(
            resource_type=RenewableType.SOLAR_PV,
            capacity_mw=100,
            capacity_factor=0.25
        )
        
        assert 'lcoe_usd_mwh' in result
        assert result['lcoe_usd_mwh'] > 0
        assert 'competitiveness' in result
    
    def test_lcoe_varies_with_capacity_factor(self, assessor):
        """Test LCOE decreases with higher capacity factor."""
        low_cf = assessor.calculate_lcoe(
            RenewableType.ONSHORE_WIND,
            capacity_mw=50,
            capacity_factor=0.25
        )
        
        high_cf = assessor.calculate_lcoe(
            RenewableType.ONSHORE_WIND,
            capacity_mw=50,
            capacity_factor=0.40
        )
        
        assert high_cf['lcoe_usd_mwh'] < low_cf['lcoe_usd_mwh']
    
    def test_lcoe_factors(self, assessor):
        """Test LCOE includes all cost factors."""
        result = assessor.calculate_lcoe(
            RenewableType.SOLAR_PV,
            capacity_mw=100,
            capacity_factor=0.25,
            discount_rate=0.08,
            lifetime_years=30
        )
        
        assert result['lifetime_years'] == 30
        assert result['discount_rate'] == 0.08


class TestStorageAnalysis:
    """Test suite for storage requirements analysis."""
    
    @pytest.fixture
    def assessor(self):
        return RenewableResourceAssessor()
    
    def test_analyze_storage_requirements(self, assessor):
        """Test storage requirement analysis."""
        # Simulate solar generation (peaks at noon)
        hours = np.arange(168)  # 1 week
        generation = np.maximum(0, 500 * np.sin(2 * np.pi * (hours % 24) / 24 - np.pi/4))
        
        # Simulate demand (two peaks)
        demand = 400 + 200 * np.sin(2 * np.pi * (hours % 24) / 24)
        
        gen_profile = xr.DataArray(generation, dims=['time'])
        demand_profile = xr.DataArray(demand, dims=['time'])
        
        result = assessor.analyze_storage_requirements(
            gen_profile,
            demand_profile,
            renewable_penetration=0.5
        )
        
        assert 'recommended_storage' in result
        assert result['recommended_storage']['power_capacity_mw'] >= 0


class TestSiteRegistry:
    """Test suite for site registry."""
    
    @pytest.fixture
    def assessor(self):
        return RenewableResourceAssessor()
    
    def test_register_site(self, assessor):
        """Test site registration."""
        site = RenewableSite(
            site_id='SOLAR_001',
            name='Desert Solar Farm',
            location=(-115.5, 33.0),
            resource_type=RenewableType.SOLAR_PV,
            capacity_mw=100,
            capacity_factor=0.28,
            annual_generation_gwh=245.3
        )
        
        result = assessor.register_site(site)
        
        assert result == 'SOLAR_001'
    
    def test_portfolio_summary(self, assessor):
        """Test portfolio summary."""
        sites = [
            RenewableSite('S1', 'Solar 1', (-115, 33), RenewableType.SOLAR_PV, 100, 0.25, 219),
            RenewableSite('S2', 'Solar 2', (-116, 34), RenewableType.SOLAR_PV, 150, 0.27, 355),
            RenewableSite('W1', 'Wind 1', (-117, 35), RenewableType.ONSHORE_WIND, 200, 0.35, 613),
        ]
        
        for site in sites:
            assessor.register_site(site)
        
        summary = assessor.get_portfolio_summary()
        
        assert summary['site_count'] == 3
        assert summary['total_capacity_mw'] == 450
        assert 'solar_pv' in summary['by_resource_type']


class TestEnums:
    """Test suite for enum types."""
    
    def test_renewable_types(self):
        """Test renewable type enum."""
        types = [
            RenewableType.SOLAR_PV,
            RenewableType.ONSHORE_WIND,
            RenewableType.HYDROPOWER
        ]
        assert len(types) == 3
    
    def test_suitability_classes(self):
        """Test suitability class enum."""
        classes = [
            SuitabilityClass.EXCELLENT,
            SuitabilityClass.GOOD,
            SuitabilityClass.MODERATE,
            SuitabilityClass.MARGINAL,
            SuitabilityClass.UNSUITABLE
        ]
        assert len(classes) == 5
