"""
Tests for the GEO-INFER-WATER quality module.
"""

import pytest
import numpy as np
import xarray as xr

from geo_infer_water.core.water_quality import (
    WaterQualityAssessor,
    WaterSample,
    WaterBodyType,
    PollutantType
)


class TestWaterQualityAssessor:
    """Test suite for WaterQualityAssessor."""
    
    @pytest.fixture
    def assessor(self):
        """Create an assessor instance."""
        return WaterQualityAssessor()
    
    def test_init(self, assessor):
        """Test initialization."""
        assert assessor.config == {}
        assert 'ph' in assessor.standards
        assert 'dissolved_oxygen' in assessor.standards
    
    def test_assess_water_quality(self, assessor):
        """Test basic water quality assessment."""
        ph = xr.DataArray([7.0, 7.5, 8.0], dims=['location'])
        
        result = assessor.assess_water_quality(ph)
        
        assert 'ph_compliant' in result
        assert all(result['ph_compliant'].values)
    
    def test_assess_water_quality_violation(self, assessor):
        """Test detection of violations."""
        ph = xr.DataArray([5.0, 7.0, 10.0], dims=['location'])  # 5.0 and 10.0 out of range
        
        result = assessor.assess_water_quality(ph)
        
        assert not all(result['ph_compliant'].values)
    
    def test_assess_multi_parameter(self, assessor):
        """Test multi-parameter assessment."""
        ph = xr.DataArray([7.0, 7.5], dims=['location'])
        do = xr.DataArray([8.0, 3.0], dims=['location'])  # Second is low
        
        result = assessor.assess_water_quality(ph, dissolved_oxygen=do)
        
        assert 'do_compliant' in result
        assert result['do_compliant'].values[0] == True
        assert result['do_compliant'].values[1] == False


class TestWaterQualityIndex:
    """Test suite for WQI calculation."""
    
    @pytest.fixture
    def assessor(self):
        return WaterQualityAssessor()
    
    @pytest.fixture
    def good_sample(self):
        return WaterSample(
            sample_id='WQ_001',
            location=(-118.25, 34.05),
            timestamp='2024-01-15T10:00:00',
            ph=7.0,
            dissolved_oxygen=8.0,
            turbidity=0.5,
            temperature=20.0,
            nitrate=2.0,
            e_coli=0
        )
    
    @pytest.fixture
    def poor_sample(self):
        return WaterSample(
            sample_id='WQ_002',
            location=(-118.25, 34.05),
            timestamp='2024-01-15T10:00:00',
            ph=5.5,
            dissolved_oxygen=3.0,
            turbidity=15.0,
            temperature=30.0,
            nitrate=25.0,
            e_coli=500
        )
    
    def test_calculate_wqi_good(self, assessor, good_sample):
        """Test WQI for good quality water."""
        result = assessor.calculate_wqi(good_sample)
        
        assert 'wqi' in result
        assert result['wqi'] > 70
        assert result['classification'] in ['Excellent', 'Good']
    
    def test_calculate_wqi_poor(self, assessor, poor_sample):
        """Test WQI for poor quality water."""
        result = assessor.calculate_wqi(poor_sample)
        
        assert result['wqi'] < 50
        assert result['classification'] in ['Medium', 'Bad', 'Very Bad']
    
    def test_wqi_sub_indices(self, assessor, good_sample):
        """Test WQI sub-indices are calculated."""
        result = assessor.calculate_wqi(good_sample)
        
        assert 'sub_indices' in result
        assert 'ph' in result['sub_indices']
        assert 'dissolved_oxygen' in result['sub_indices']


class TestPollutionTracking:
    """Test suite for pollution tracking."""
    
    @pytest.fixture
    def assessor(self):
        return WaterQualityAssessor()
    
    def test_identify_pollution_sources(self, assessor):
        """Test pollution source identification."""
        concentration = xr.DataArray(
            [[1, 2, 3], [4, 95, 6], [7, 8, 9]],
            dims=['x', 'y']
        )
        
        result = assessor.identify_pollution_sources(concentration)
        
        assert 'pollution_hotspots' in result
        assert 'potential_sources' in result
    
    def test_track_pollution_plume(self, assessor):
        """Test pollution plume tracking."""
        result = assessor.track_pollution_plume(
            initial_location=(-118.25, 34.05),
            pollutant_type=PollutantType.NUTRIENT,
            flow_velocity=(0.1, 0.05),
            diffusion_coefficient=10.0,
            time_hours=24
        )
        
        assert 'plume_center' in result
        assert 'plume_area_km2' in result
        assert 'dispersion_sigma_m' in result


class TestTrendAnalysis:
    """Test suite for trend analysis."""
    
    @pytest.fixture
    def assessor(self):
        return WaterQualityAssessor()
    
    @pytest.fixture
    def samples(self):
        return [
            WaterSample(
                sample_id=f'WQ_{i}',
                location=(-118.25, 34.05),
                timestamp=f'2024-01-{i+1:02d}T10:00:00',
                ph=7.0 + i * 0.1,  # Increasing trend
                dissolved_oxygen=8.0 - i * 0.2,  # Decreasing trend
                turbidity=0.5,
                temperature=20.0
            )
            for i in range(10)
        ]
    
    def test_analyze_trends(self, assessor, samples):
        """Test trend analysis."""
        result = assessor.analyze_trends(samples, 'ph')
        
        assert result['parameter'] == 'ph'
        assert result['sample_count'] == 10
        assert result['trend_direction'] == 'increasing'
    
    def test_analyze_trends_decreasing(self, assessor, samples):
        """Test decreasing trend detection."""
        result = assessor.analyze_trends(samples, 'dissolved_oxygen')
        
        assert result['trend_direction'] in ['decreasing', 'stable']
    
    def test_analyze_trends_empty(self, assessor):
        """Test trend analysis with empty data."""
        result = assessor.analyze_trends([], 'ph')
        
        assert 'error' in result


class TestRiskAssessment:
    """Test suite for risk assessment."""
    
    @pytest.fixture
    def assessor(self):
        return WaterQualityAssessor()
    
    @pytest.fixture
    def safe_samples(self):
        return [
            WaterSample(
                sample_id=f'WQ_{i}',
                location=(-118.25, 34.05),
                timestamp='2024-01-15T10:00:00',
                ph=7.0,
                dissolved_oxygen=8.0,
                turbidity=0.5,
                temperature=20.0,
                e_coli=0
            )
            for i in range(5)
        ]
    
    @pytest.fixture
    def risky_samples(self):
        return [
            WaterSample(
                sample_id=f'WQ_{i}',
                location=(-118.25, 34.05),
                timestamp='2024-01-15T10:00:00',
                ph=5.0,  # Too low
                dissolved_oxygen=3.0,  # Too low
                turbidity=10.0,  # Too high
                temperature=35.0,  # Too high
                e_coli=500  # Too high
            )
            for i in range(5)
        ]
    
    def test_assess_risk_low(self, assessor, safe_samples):
        """Test low risk assessment."""
        result = assessor.assess_risk(
            safe_samples,
            WaterBodyType.RIVER,
            usage_type='drinking'
        )
        
        assert result['risk_level'] == 'Low'
        assert result['risk_score'] < 0.5
    
    def test_assess_risk_high(self, assessor, risky_samples):
        """Test high risk assessment."""
        result = assessor.assess_risk(
            risky_samples,
            WaterBodyType.LAKE,
            usage_type='recreation'
        )
        
        assert result['risk_level'] in ['High', 'Critical']
        assert result['violation_count'] > 0


class TestRegulatoryCompliance:
    """Test suite for regulatory compliance."""
    
    @pytest.fixture
    def assessor(self):
        return WaterQualityAssessor()
    
    @pytest.fixture
    def compliant_samples(self):
        return [
            WaterSample(
                sample_id='WQ_001',
                location=(-118.25, 34.05),
                timestamp='2024-01-15T10:00:00',
                ph=7.0,
                dissolved_oxygen=8.0,
                turbidity=0.5,
                temperature=20.0,
                nitrate=5.0,
                e_coli=0
            )
        ]
    
    def test_check_compliance_epa(self, assessor, compliant_samples):
        """Test EPA compliance check."""
        result = assessor.check_regulatory_compliance(compliant_samples, 'EPA')
        
        assert result['regulations'] == 'EPA'
        assert result['overall_compliant'] == True
    
    def test_check_compliance_who(self, assessor, compliant_samples):
        """Test WHO compliance check."""
        result = assessor.check_regulatory_compliance(compliant_samples, 'WHO')
        
        assert result['regulations'] == 'WHO'
        assert 'results' in result


class TestPollutantLoad:
    """Test suite for pollutant load calculation."""
    
    @pytest.fixture
    def assessor(self):
        return WaterQualityAssessor()
    
    def test_calculate_pollutant_load(self, assessor):
        """Test pollutant load calculation."""
        result = assessor.calculate_pollutant_load(
            concentration_mg_l=10.0,
            flow_rate_m3_s=5.0,
            time_period_hours=24.0
        )
        
        assert 'load_kg' in result
        assert result['load_kg'] > 0
        assert result['load_kg_per_day'] == result['load_kg']  # 24 hours
    
    def test_calculate_pollutant_load_short_period(self, assessor):
        """Test load calculation for short period."""
        result = assessor.calculate_pollutant_load(
            concentration_mg_l=5.0,
            flow_rate_m3_s=2.0,
            time_period_hours=1.0
        )
        
        # Daily load should be 24x the hourly load
        assert result['load_kg_per_day'] == pytest.approx(result['load_kg'] * 24)


class TestEnums:
    """Test suite for enum types."""
    
    def test_water_body_types(self):
        """Test water body types enum."""
        types = [
            WaterBodyType.RIVER,
            WaterBodyType.LAKE,
            WaterBodyType.RESERVOIR,
            WaterBodyType.GROUNDWATER
        ]
        assert len(types) == 4
    
    def test_pollutant_types(self):
        """Test pollutant types enum."""
        types = [
            PollutantType.NUTRIENT,
            PollutantType.ORGANIC,
            PollutantType.PATHOGEN,
            PollutantType.HEAVY_METAL
        ]
        assert len(types) == 4
