"""Unit tests for climate data processing."""

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from geo_infer_climate.core.climate_data import ClimateDataProcessor


def test_climate_data_processor_init():
    """Test ClimateDataProcessor initialization."""
    processor = ClimateDataProcessor()
    assert processor is not None
    assert processor.supported_formats is not None
    assert processor.supported_datasets is not None


def test_validate_dataset():
    """Test dataset validation."""
    processor = ClimateDataProcessor()
    
    # Create test dataset
    time = pd.date_range('2000-01-01', periods=10, freq='D')
    lat = np.linspace(-90, 90, 10)
    lon = np.linspace(-180, 180, 10)
    
    data = xr.Dataset({
        'temperature': (['time', 'lat', 'lon'], np.random.randn(10, 10, 10))
    }, coords={'time': time, 'lat': lat, 'lon': lon})
    
    results = processor.validate_dataset(data)
    assert results['has_coordinates'] is True
    assert results['has_time_dimension'] is True
    assert results['has_spatial_dimensions'] is True


def test_extract_temporal_subset():
    """Test temporal subsetting."""
    processor = ClimateDataProcessor()
    
    time = pd.date_range('2000-01-01', periods=100, freq='D')
    data = xr.Dataset({
        'temperature': (['time'], np.random.randn(100))
    }, coords={'time': time})
    
    subset = processor.extract_temporal_subset(
        data,
        '2000-01-10',
        '2000-01-20'
    )
    
    assert len(subset.time) == 11


def test_extract_spatial_subset():
    """Test spatial subsetting."""
    processor = ClimateDataProcessor()
    
    lat = np.linspace(-90, 90, 20)
    lon = np.linspace(-180, 180, 20)
    data = xr.Dataset({
        'temperature': (['lat', 'lon'], np.random.randn(20, 20))
    }, coords={'lat': lat, 'lon': lon})
    
    subset = processor.extract_spatial_subset(
        data,
        (-45, 45),
        (-90, 90)
    )
    
    assert len(subset.lat) < len(data.lat)

