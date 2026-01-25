"""
Tests for the GEO-INFER-CLIMATE extreme events module.
"""

import pytest
import numpy as np
import xarray as xr

from geo_infer_climate.core.extreme_events import (
    ExtremeEventAnalyzer,
    ExtremeEventType,
    Severity,
    ExtremeEvent
)


class TestExtremeEventAnalyzer:
    """Test suite for ExtremeEventAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        return ExtremeEventAnalyzer()
    
    @pytest.fixture
    def temperature_data(self):
        np.random.seed(42)
        values = 20 + 10 * np.sin(np.linspace(0, 4*np.pi, 365)) + np.random.normal(0, 3, 365)
        return xr.DataArray(values, dims=['time'])
    
    @pytest.fixture
    def precipitation_data(self):
        np.random.seed(42)
        return xr.DataArray(np.random.exponential(5, 365), dims=['time'])
    
    def test_init(self, analyzer):
        """Test initialization."""
        assert analyzer.config == {}
        assert 'heatwave_percentile' in analyzer.thresholds


class TestColdSpellDetection:
    """Test suite for cold spell detection."""
    
    @pytest.fixture
    def analyzer(self):
        return ExtremeEventAnalyzer()
    
    @pytest.fixture
    def cold_data(self):
        values = [10] * 30 + [-5] * 10 + [10] * 30
        return xr.DataArray(values, dims=['time'])
    
    def test_detect_cold_spells(self, analyzer, cold_data):
        """Test cold spell detection."""
        result = analyzer.detect_cold_spells(cold_data)
        
        assert result['events_detected'] >= 1
        assert 'threshold_temp' in result
    
    def test_cold_spell_duration(self, analyzer, cold_data):
        """Test cold spell duration calculation."""
        result = analyzer.detect_cold_spells(cold_data, min_duration=3)
        
        if result['events']:
            event = result['events'][0]
            assert 'duration_days' in event
            assert event['duration_days'] >= 3


class TestFloodDetection:
    """Test suite for flood detection."""
    
    @pytest.fixture
    def analyzer(self):
        return ExtremeEventAnalyzer()
    
    @pytest.fixture
    def streamflow_data(self):
        values = [50] * 30 + [200] * 5 + [50] * 30
        return xr.DataArray(values, dims=['time'])
    
    def test_detect_floods(self, analyzer, streamflow_data):
        """Test flood detection."""
        result = analyzer.detect_floods(streamflow_data)
        
        assert result['events_detected'] >= 1
        assert 'threshold_flow' in result
    
    def test_flood_peak_value(self, analyzer, streamflow_data):
        """Test flood peak is captured."""
        result = analyzer.detect_floods(streamflow_data)
        
        if result['events']:
            assert result['max_peak'] == 200


class TestReturnPeriod:
    """Test suite for return period calculation."""
    
    @pytest.fixture
    def analyzer(self):
        return ExtremeEventAnalyzer()
    
    @pytest.fixture
    def historical_data(self):
        np.random.seed(42)
        return xr.DataArray(np.random.normal(100, 20, 1000), dims=['time'])
    
    def test_calculate_return_period_empirical(self, analyzer, historical_data):
        """Test empirical return period."""
        result = analyzer.calculate_return_period(
            historical_data,
            value=150,
            method='empirical'
        )
        
        assert 'return_period_years' in result
        assert 'severity' in result
    
    def test_calculate_return_period_gumbel(self, analyzer, historical_data):
        """Test Gumbel return period."""
        result = analyzer.calculate_return_period(
            historical_data,
            value=180,
            method='gumbel'
        )
        
        assert result['method'] == 'gumbel'
        assert result['return_period_years'] is not None
    
    def test_severity_classification(self, analyzer, historical_data):
        """Test severity is classified correctly."""
        # Extreme value should get high severity
        result = analyzer.calculate_return_period(
            historical_data,
            value=200,  # Very extreme
            method='gev'
        )
        
        assert result['severity'] in ['severe', 'extreme', 'catastrophic']


class TestCompoundEvents:
    """Test suite for compound event detection."""
    
    @pytest.fixture
    def analyzer(self):
        return ExtremeEventAnalyzer()
    
    def test_detect_compound_events(self, analyzer):
        """Test compound event detection."""
        temp = xr.DataArray([20, 35, 36, 35, 20, 20], dims=['time'])
        precip = xr.DataArray([10, 0, 0.5, 0.2, 10, 5], dims=['time'])
        
        result = analyzer.detect_compound_events(temp, precip)
        
        assert 'compound_type' in result
        assert 'compound_days' in result
        assert 'correlation' in result
    
    def test_compound_frequency(self, analyzer):
        """Test compound frequency calculation."""
        temp = xr.DataArray([35] * 50 + [20] * 50, dims=['time'])
        precip = xr.DataArray([0.1] * 50 + [10] * 50, dims=['time'])
        
        result = analyzer.detect_compound_events(temp, precip)
        
        assert result['compound_frequency'] > 0


class TestClimateIndices:
    """Test suite for climate indices."""
    
    @pytest.fixture
    def analyzer(self):
        return ExtremeEventAnalyzer()
    
    def test_calculate_climate_indices_temp_only(self, analyzer):
        """Test indices with temperature only."""
        temp = xr.DataArray(np.random.uniform(-5, 35, 365), dims=['time'])
        
        result = analyzer.calculate_climate_indices(temp)
        
        assert 'TXx' in result['indices']
        assert 'TNn' in result['indices']
        assert 'SU25' in result['indices']
        assert 'FD0' in result['indices']
    
    def test_calculate_climate_indices_with_precip(self, analyzer):
        """Test indices with precipitation."""
        temp = xr.DataArray(np.random.uniform(10, 30, 365), dims=['time'])
        precip = xr.DataArray(np.random.exponential(5, 365), dims=['time'])
        
        result = analyzer.calculate_climate_indices(temp, precip)
        
        assert 'PRCPTOT' in result['indices']
        assert 'RX1day' in result['indices']
        assert 'CDD' in result['indices']
        assert 'CWD' in result['indices']


class TestEventRegistry:
    """Test suite for event registry."""
    
    @pytest.fixture
    def analyzer(self):
        return ExtremeEventAnalyzer()
    
    def test_register_event(self, analyzer):
        """Test event registration."""
        event = ExtremeEvent(
            event_id='HW_2024_001',
            event_type=ExtremeEventType.HEATWAVE,
            start_date='2024-07-15',
            end_date='2024-07-20',
            duration_days=5,
            peak_value=42.5,
            severity=Severity.SEVERE
        )
        
        result = analyzer.register_event(event)
        assert result == 'HW_2024_001'
    
    def test_get_event_statistics(self, analyzer):
        """Test event statistics."""
        events = [
            ExtremeEvent('HW1', ExtremeEventType.HEATWAVE, '2024-06', '2024-06', 5, 40, Severity.MODERATE),
            ExtremeEvent('HW2', ExtremeEventType.HEATWAVE, '2024-07', '2024-07', 7, 42, Severity.SEVERE),
            ExtremeEvent('DR1', ExtremeEventType.DROUGHT, '2024-08', '2024-09', 30, 0.5, Severity.SEVERE),
        ]
        
        for event in events:
            analyzer.register_event(event)
        
        stats = analyzer.get_event_statistics()
        
        assert stats['total_events'] == 3
        assert 'heatwave' in stats['by_type']


class TestEnums:
    """Test enum types."""
    
    def test_extreme_event_types(self):
        types = [
            ExtremeEventType.HEATWAVE,
            ExtremeEventType.DROUGHT,
            ExtremeEventType.FLOOD,
            ExtremeEventType.COMPOUND
        ]
        assert len(types) == 4
    
    def test_severity_levels(self):
        severities = [
            Severity.MINOR,
            Severity.MODERATE,
            Severity.SEVERE,
            Severity.EXTREME,
            Severity.CATASTROPHIC
        ]
        assert len(severities) == 5
