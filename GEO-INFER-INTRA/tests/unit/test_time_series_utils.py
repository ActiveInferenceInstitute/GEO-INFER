"""Unit tests for time series utilities."""

import pytest
import math
import sys
import os
import datetime
from pathlib import Path

# Add parent directory to the path to find our utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tests.utils.time_series import (
    create_iso8601_timestamp, create_timestamp_range, create_daily_timestamps,
    create_hourly_timestamps, create_time_series_data, random_walk_generator,
    seasonal_generator
)

@pytest.mark.unit
class TestTimeSeriesUtils:
    """Test suite for time series utilities."""
    
    def test_create_iso8601_timestamp(self):
        """Test creating an ISO8601 timestamp."""
        # Test with default values
        timestamp = create_iso8601_timestamp(2023, 1, 1)
        assert timestamp == "2023-01-01T00:00:00.000Z"
        
        # Test with custom time values
        timestamp = create_iso8601_timestamp(2023, 1, 1, 12, 30, 45, 123456)
        assert timestamp == "2023-01-01T12:30:45.123Z"
        
        # Test with timezone
        timestamp = create_iso8601_timestamp(2023, 1, 1, timezone="+01:00")
        assert timestamp == "2023-01-01T00:00:00.000+01:00"
    
    def test_create_timestamp_range(self):
        """Test creating a range of timestamps."""
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 1, 5)
        interval = datetime.timedelta(days=1)
        
        timestamps = create_timestamp_range(start_date, end_date, interval)
        
        assert len(timestamps) == 5
        assert timestamps[0] == "2023-01-01T00:00:00.000Z"
        assert timestamps[-1] == "2023-01-05T00:00:00.000Z"
    
    def test_create_daily_timestamps(self):
        """Test creating daily timestamps."""
        timestamps = create_daily_timestamps(2023, 1, 1, 5)
        
        assert len(timestamps) == 5
        assert timestamps[0] == "2023-01-01T00:00:00.000Z"
        assert timestamps[-1] == "2023-01-05T00:00:00.000Z"
    
    def test_create_hourly_timestamps(self):
        """Test creating hourly timestamps."""
        timestamps = create_hourly_timestamps(2023, 1, 1, 0, 5)
        
        assert len(timestamps) == 5
        assert timestamps[0] == "2023-01-01T00:00:00.000Z"
        assert timestamps[-1] == "2023-01-01T04:00:00.000Z"
    
    def test_create_time_series_data(self):
        """Test creating time series data."""
        timestamps = create_daily_timestamps(2023, 1, 1, 5)
        
        # Create a simple value generator
        def value_generator(timestamp, index):
            return 10 + index
        
        time_series = create_time_series_data(timestamps, value_generator)
        
        assert "timestamps" in time_series
        assert "values" in time_series
        assert len(time_series["timestamps"]) == 5
        assert len(time_series["values"]) == 5
        assert time_series["values"] == [10, 11, 12, 13, 14]
    
    def test_random_walk_generator(self):
        """Test random walk generator."""
        # Test with initial value
        value = random_walk_generator("2023-01-01T00:00:00Z", 0, start_value=10.0)
        assert value == 10.0
        
        # Test subsequent values
        values = [random_walk_generator("", i, start_value=10.0, step_size=0.5) for i in range(5)]
        
        # Values should increase or decrease randomly, but should not be exactly equal
        for i in range(1, len(values)):
            assert values[i] != values[i-1]
    
    def test_seasonal_generator(self):
        """Test seasonal generator."""
        # Generate values for a full period
        period = 24
        values = [seasonal_generator("", i, base_value=10.0, amplitude=2.0, period=period, noise_level=0.0) for i in range(period)]
        
        # First and last values should be approximately equal (full cycle)
        assert abs(values[0] - values[-1]) < 0.01
        
        # Peak should be at 1/4 period (sin wave peaks at π/2)
        peak_index = period // 4
        assert values[peak_index] == max(values)
        
        # Trough should be at 3/4 period (sin wave troughs at 3π/2)
        trough_index = 3 * period // 4
        assert values[trough_index] == min(values) 