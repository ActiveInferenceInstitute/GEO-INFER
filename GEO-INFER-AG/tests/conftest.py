"""Common test fixtures for GEO-INFER-AG tests."""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import pytest
from shapely.geometry import Polygon, Point
from datetime import datetime, timedelta

# Define constants for test data
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "geospatial")

# Create the test data directory if it doesn't exist
os.makedirs(TEST_DATA_DIR, exist_ok=True)


@pytest.fixture
def sample_field_data():
    """Create a sample GeoDataFrame with field data for testing."""
    # Create sample field geometries
    geometries = [
        Polygon([(0, 0), (0, 10), (10, 10), (10, 0)]),
        Polygon([(20, 0), (20, 5), (25, 5), (25, 0)]),
        Polygon([(30, 10), (30, 20), (40, 20), (40, 10)])
    ]
    
    # Create sample field data
    data = {
        "field_id": ["field_1", "field_2", "field_3"],
        "name": ["Field 1", "Field 2", "Field 3"],
        "crop_type": ["corn", "wheat", "soybean"],
        "area_ha": [10.0, 2.5, 10.0],
        "geometry": geometries
    }
    
    # Create GeoDataFrame
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_soil_data():
    """Create a sample GeoDataFrame with soil data for testing."""
    # Create sample soil geometries
    geometries = [
        Point(5, 5),
        Point(22.5, 2.5),
        Point(35, 15)
    ]
    
    # Create sample soil data
    data = {
        "field_id": ["field_1", "field_2", "field_3"],
        "organic_matter": [2.5, 1.8, 3.2],
        "ph": [6.5, 7.2, 6.0],
        "bulk_density": [1.3, 1.4, 1.2],
        "geometry": geometries
    }
    
    # Create GeoDataFrame
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_weather_data():
    """Create a sample DataFrame with weather data for testing."""
    # Create date range
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    # Create sample weather data
    data = {
        "date": dates,
        "temperature": np.random.uniform(15, 30, len(dates)),  # °C
        "precipitation": np.random.uniform(0, 10, len(dates)),  # mm
        "solar_radiation": np.random.uniform(10, 25, len(dates)),  # MJ/m²/day
        "humidity": np.random.uniform(40, 90, len(dates)),  # %
        "wind_speed": np.random.uniform(1, 5, len(dates))  # m/s
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df.set_index("date")


@pytest.fixture
def sample_management_data():
    """Create a sample DataFrame with management data for testing."""
    # Create sample management data
    data = {
        "field_id": ["field_1", "field_2", "field_3"],
        "planting_date": [
            datetime.now() - timedelta(days=60),
            datetime.now() - timedelta(days=90),
            datetime.now() - timedelta(days=45)
        ],
        "fertilizer_applied_kg_ha": [200, 150, 180],
        "irrigation_applied_mm": [50, 0, 30],
        "tillage_type": ["reduced_till", "no_till", "conventional_till"]
    }
    
    # Create DataFrame
    return pd.DataFrame(data)


@pytest.fixture
def sample_time_series_data():
    """Create a sample DataFrame with time series data for testing."""
    # Create date range
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=120),
        end=datetime.now(),
        freq='D'
    )
    
    # Create sample NDVI time series with a growing season pattern
    days = np.arange(len(dates))
    ndvi = 0.2 + 0.6 * np.sin(np.pi * days / 90) ** 2
    ndvi = ndvi + np.random.normal(0, 0.05, len(dates))
    ndvi = np.clip(ndvi, 0.1, 0.9)
    
    # Create sample EVI time series
    evi = 0.15 + 0.7 * np.sin(np.pi * days / 90) ** 2
    evi = evi + np.random.normal(0, 0.05, len(dates))
    evi = np.clip(evi, 0.1, 0.85)
    
    # Create sample data
    data = {
        "date": dates,
        "ndvi": ndvi,
        "evi": evi
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df.set_index("date")


@pytest.fixture
def management_practices():
    """Create sample management practices dictionary for testing."""
    return {
        "field_1": ["no_till", "cover_crops", "precision_agriculture"],
        "field_2": ["reduced_till", "crop_rotation"],
        "field_3": ["conventional_till", "organic_fertilizer"]
    } 