"""
Tests for the GEO-INFER-TIME event detection module.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from geo_infer_time.core.event_detection import EventDetector
from geo_infer_time.models.timeseries import TimeSeries


class MockTimeSeries:
    """Mock TimeSeries for testing."""
    
    def __init__(self, values, frequency='D'):
        self.values = values
        self.frequency = frequency
        
    def to_dataframe(self):
        dates = pd.date_range('2024-01-01', periods=len(self.values), freq='D')
        return pd.DataFrame({'value': self.values}, index=dates)


class TestEventDetector:
    """Test suite for EventDetector."""
    
    @pytest.fixture
    def detector(self):
        return EventDetector(threshold_multiplier=3.0, window_size=10)
    
    @pytest.fixture
    def normal_series(self):
        # Normal distributed series
        np.random.seed(42)
        values = [50 + np.random.normal(0, 5) for _ in range(100)]
        return MockTimeSeries(values)
    
    @pytest.fixture
    def series_with_anomalies(self):
        np.random.seed(42)
        values = [50 + np.random.normal(0, 5) for _ in range(100)]
        # Insert clear anomalies
        values[25] = 150  # Large positive outlier
        values[75] = -50  # Large negative outlier
        return MockTimeSeries(values)
    
    @pytest.fixture
    def series_with_changepoint(self):
        # Series with clear level shift at index 50
        values = [10 + np.random.normal(0, 1) for _ in range(50)]
        values += [50 + np.random.normal(0, 1) for _ in range(50)]
        return MockTimeSeries(values)


class TestAnomalyDetection:
    """Test anomaly detection methods."""
    
    @pytest.fixture
    def detector(self):
        return EventDetector(threshold_multiplier=3.0, window_size=10)
    
    @pytest.fixture
    def series_with_anomalies(self):
        np.random.seed(42)
        values = [50 + np.random.normal(0, 5) for _ in range(100)]
        values[25] = 150
        values[75] = -50
        return MockTimeSeries(values)
    
    def test_detect_anomalies_zscore(self, detector, series_with_anomalies):
        """Test z-score anomaly detection."""
        result = detector.detect_anomalies(series_with_anomalies, method='z_score')
        
        assert 'method' in result
        assert result['method'] == 'z_score'
        assert 'anomalies' in result
        assert 'count' in result
        assert result['count'] >= 2  # Should detect at least both inserted anomalies
    
    def test_detect_anomalies_iqr(self, detector, series_with_anomalies):
        """Test IQR anomaly detection."""
        result = detector.detect_anomalies(series_with_anomalies, method='iqr')
        
        assert result['method'] == 'iqr'
        assert 'anomalies' in result
        assert result['count'] >= 2
    
    def test_anomaly_structure(self, detector, series_with_anomalies):
        """Test anomaly result structure."""
        result = detector.detect_anomalies(series_with_anomalies, method='z_score')
        
        if result['anomalies']:
            anomaly = result['anomalies'][0]
            assert 'timestamp' in anomaly
            assert 'value' in anomaly
            assert 'type' in anomaly
    
    def test_no_anomalies_in_normal_series(self, detector):
        """Test that normal series has few or no anomalies."""
        np.random.seed(123)
        # Tightly distributed values
        values = [50 + np.random.normal(0, 0.5) for _ in range(100)]
        series = MockTimeSeries(values)
        
        result = detector.detect_anomalies(series, method='z_score')
        # Very tight distribution should have few anomalies
        assert result['count'] <= 5
    
    def test_invalid_method_raises(self, detector):
        """Test that invalid method raises ValueError."""
        values = [50] * 100
        series = MockTimeSeries(values)
        
        with pytest.raises(ValueError, match="Unknown anomaly detection method"):
            detector.detect_anomalies(series, method='invalid_method')


class TestChangepointDetection:
    """Test changepoint detection methods."""
    
    @pytest.fixture
    def detector(self):
        return EventDetector(threshold_multiplier=2.0, window_size=10)
    
    @pytest.fixture
    def series_with_changepoint(self):
        values = [10 + np.random.normal(0, 1) for _ in range(50)]
        values += [50 + np.random.normal(0, 1) for _ in range(50)]
        return MockTimeSeries(values)
    
    def test_detect_changepoints_basic(self, detector, series_with_changepoint):
        """Test basic changepoint detection."""
        result = detector.detect_changepoints(series_with_changepoint, sensitivity=0.5)
        
        assert 'changepoints' in result
        assert 'count' in result
        assert result['count'] >= 1
    
    def test_changepoint_structure(self, detector, series_with_changepoint):
        """Test changepoint result structure."""
        result = detector.detect_changepoints(series_with_changepoint, sensitivity=0.3)
        
        if result['changepoints']:
            cp = result['changepoints'][0]
            assert 'timestamp' in cp
            assert 'index' in cp
            assert 'mean_change' in cp
            assert 'mean_before' in cp
            assert 'mean_after' in cp
    
    def test_changepoint_near_transition(self, detector, series_with_changepoint):
        """Test that changepoint is detected near actual transition."""
        result = detector.detect_changepoints(series_with_changepoint, sensitivity=0.2)
        
        if result['changepoints']:
            # At least one changepoint should be near index 50
            indices = [cp['index'] for cp in result['changepoints']]
            near_transition = any(40 <= idx <= 60 for idx in indices)
            assert near_transition
    
    def test_no_changepoints_in_stable_series(self, detector):
        """Test that stable series has few changepoints."""
        # Constant series
        values = [50.0 + np.random.normal(0, 0.1) for _ in range(100)]
        series = MockTimeSeries(values)
        
        result = detector.detect_changepoints(series, sensitivity=5.0)
        # With high sensitivity threshold, stable series should have few changepoints
        assert result['count'] <= 10


class TestEventDetectorConfiguration:
    """Test EventDetector configuration options."""
    
    def test_custom_threshold(self):
        """Test detector with custom threshold."""
        detector = EventDetector(threshold_multiplier=2.0)
        assert detector.threshold_multiplier == 2.0
    
    def test_custom_window_size(self):
        """Test detector with custom window size."""
        detector = EventDetector(window_size=20)
        assert detector.window_size == 20
    
    def test_sensitivity_affects_changepoints(self):
        """Test that sensitivity parameter affects changepoint detection."""
        values = [10 + np.random.normal(0, 2) for _ in range(50)]
        values += [15 + np.random.normal(0, 2) for _ in range(50)]  # Small shift
        series = MockTimeSeries(values)
        
        detector = EventDetector(window_size=10)
        
        # Low sensitivity should detect more changepoints
        result_low = detector.detect_changepoints(series, sensitivity=0.1)
        # High sensitivity should detect fewer
        result_high = detector.detect_changepoints(series, sensitivity=5.0)
        
        assert result_low['count'] >= result_high['count']
