"""
Pytest fixtures for GEO-INFER-WATER tests.

Provides watershed GeoDataFrames, streamflow time series,
water quality data, and standard spatial fixtures.
"""
import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pathlib import Path
from typing import List, Dict, Any, Tuple


@pytest.fixture(scope="session")
def sample_coordinates() -> List[Tuple[float, float]]:
    """Standard (lat, lng) coordinate pairs for spatial tests."""
    return [
        (47.6062, -122.3321),
        (37.7749, -122.4194),
        (40.7128, -74.0060),
        (51.5074, -0.1278),
        (35.6762, 139.6503),
    ]


@pytest.fixture(scope="function")
def sample_geodataframe() -> gpd.GeoDataFrame:
    """Standard GeoDataFrame with EPSG:4326 for spatial tests."""
    return gpd.GeoDataFrame(
        {"id": range(5), "value": np.random.uniform(0, 100, 5)},
        geometry=[Point(-122.33 + i * 0.01, 47.61 + i * 0.01) for i in range(5)],
        crs="EPSG:4326",
    )


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary directory for test output files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def watershed_gdf() -> gpd.GeoDataFrame:
    """GeoDataFrame with a polygon watershed boundary for hydrology tests.

    Contains a simplified polygon representing a small watershed in the
    Cascades with drainage area, mean elevation, and land cover attributes.
    """
    watershed = Polygon([
        (-121.8, 47.2), (-121.6, 47.15),
        (-121.4, 47.2), (-121.3, 47.35),
        (-121.4, 47.5), (-121.6, 47.55),
        (-121.8, 47.5), (-121.9, 47.35),
    ])

    return gpd.GeoDataFrame(
        {
            "watershed_id": ["WS_CASCADE_001"],
            "name": ["Upper Cedar River"],
            "drainage_area_km2": [185.3],
            "mean_elevation_m": [820.0],
            "forest_cover_pct": [78.5],
            "impervious_pct": [3.2],
            "huc12": ["171100110101"],
        },
        geometry=[watershed],
        crs="EPSG:4326",
    )


@pytest.fixture
def streamflow_series() -> pd.Series:
    """365-day daily streamflow time series in cubic meters per second.

    Simulates a Pacific Northwest mountain stream with spring snowmelt
    peak (April-May), low baseflow in late summer (August-September),
    and fall rain events (October-November).
    """
    rng = np.random.default_rng(seed=42)
    dates = pd.date_range("2024-01-01", periods=365, freq="D", tz="UTC")
    day_of_year = np.arange(365)

    # Baseflow with seasonal signal
    baseflow = 5.0 + 3.0 * np.sin(2 * np.pi * (day_of_year - 30) / 365)
    # Spring snowmelt peak (days 90-150)
    snowmelt = 15.0 * np.exp(-0.5 * ((day_of_year - 120) / 20) ** 2)
    # Fall rain bump (days 270-330)
    fall_rain = 8.0 * np.exp(-0.5 * ((day_of_year - 300) / 15) ** 2)
    # Random daily variability
    noise = rng.exponential(1.5, 365)

    flow = baseflow + snowmelt + fall_rain + noise
    flow = np.maximum(flow, 0.5)  # Minimum flow

    return pd.Series(flow.round(2), index=dates, name="discharge_cms")


@pytest.fixture
def water_quality_data() -> Dict[str, Any]:
    """Water quality measurement data for water analysis tests.

    Contains measurements for multiple parameters at a monitoring
    station with values, units, and regulatory thresholds.
    """
    return {
        "station_id": "WQ_STN_042",
        "sample_date": "2024-07-15",
        "parameters": {
            "dissolved_oxygen_mg_l": {
                "value": 8.5,
                "threshold": 6.5,
                "status": "compliant",
            },
            "temperature_c": {
                "value": 16.2,
                "threshold": 18.0,
                "status": "compliant",
            },
            "ph": {
                "value": 7.4,
                "threshold_range": [6.5, 8.5],
                "status": "compliant",
            },
            "turbidity_ntu": {
                "value": 12.3,
                "threshold": 25.0,
                "status": "compliant",
            },
            "total_nitrogen_mg_l": {
                "value": 1.8,
                "threshold": 2.0,
                "status": "compliant",
            },
            "e_coli_cfu_100ml": {
                "value": 85,
                "threshold": 126,
                "status": "compliant",
            },
        },
    }
