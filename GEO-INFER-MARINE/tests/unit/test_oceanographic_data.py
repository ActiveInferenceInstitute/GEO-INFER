"""
Unit tests for oceanographic data processing.
"""

import pytest
from geo_infer_marine.core.oceanographic_data import OceanographicDataProcessor


class TestOceanographicDataProcessor:
    """Test suite for OceanographicDataProcessor."""
    
    def test_initialization(self):
        """Test processor initialization."""
        processor = OceanographicDataProcessor()
        assert processor is not None
    
    def test_process_temperature_data(self):
        """Test temperature data processing."""
        processor = OceanographicDataProcessor()
        result = processor.process_temperature_data(
            temperature_data=[20.0, 21.0, 22.0],
            depth_levels=[0, 10, 20]
        )
        assert result is not None

