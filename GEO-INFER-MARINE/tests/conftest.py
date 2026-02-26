"""
Pytest fixtures for GEO-INFER-MARINE tests.

Provides coastal polygon GeoDataFrames, bathymetry grids,
sea surface temperature time series, and standard spatial fixtures.
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
def coastal_polygon_gdf() -> gpd.GeoDataFrame:
    """GeoDataFrame with a shoreline polygon for coastal analysis.

    Contains a simplified polygon representing a section of the
    Pacific Northwest coast with shoreline type and erosion rate
    attributes.
    """
    # Simplified coastal polygon near Olympic Peninsula
    coast = Polygon([
        (-124.7, 47.5), (-124.5, 47.5),
        (-124.4, 47.6), (-124.3, 47.7),
        (-124.4, 47.8), (-124.6, 47.8),
        (-124.7, 47.7), (-124.7, 47.5),
    ])

    return gpd.GeoDataFrame(
        {
            "coast_id": ["OLY_001"],
            "shoreline_type": ["rocky"],
            "erosion_rate_m_yr": [0.15],
            "length_km": [42.5],
            "protected_status": ["national_park"],
        },
        geometry=[coast],
        crs="EPSG:4326",
    )


@pytest.fixture
def bathymetry_grid() -> Dict[str, Any]:
    """Bathymetry grid with depth values for marine spatial analysis.

    Contains a 20x20 grid of ocean depth values (negative meters)
    representing a continental shelf transect from shore to deep water,
    with coordinate bounds and resolution metadata.
    """
    rng = np.random.default_rng(seed=42)
    rows, cols = 20, 20

    # Depth increases from east (shore) to west (open ocean)
    x = np.linspace(0, 1, cols)
    y = np.linspace(0, 1, rows)
    xx, yy = np.meshgrid(x, y)
    depth = -10.0 - 200.0 * xx + rng.normal(0, 5, (rows, cols))
    depth = np.clip(depth, -500, -1)

    return {
        "depth_m": depth,
        "bounds": {
            "north": 48.0,
            "south": 47.0,
            "east": -124.0,
            "west": -125.0,
        },
        "resolution_degrees": 0.05,
        "crs": "EPSG:4326",
        "source": "synthetic_test_data",
    }


@pytest.fixture
def sst_time_series() -> pd.Series:
    """365-day daily sea surface temperature time series.

    Simulates SST for a North Pacific location with annual cycle
    (peak in August, trough in February), realistic range of 7-16C,
    and daily variability.
    """
    rng = np.random.default_rng(seed=42)
    dates = pd.date_range("2024-01-01", periods=365, freq="D", tz="UTC")
    day_of_year = np.arange(365)

    # SST annual cycle: cooler in winter, warmer in summer
    sst = 11.5 + 4.5 * np.sin(2 * np.pi * (day_of_year - 45) / 365)
    sst += rng.normal(0, 0.8, 365)

    return pd.Series(sst.round(2), index=dates, name="sst_celsius")


@pytest.fixture
def marine_species_gdf() -> gpd.GeoDataFrame:
    """GeoDataFrame with marine species observation points.

    Contains 20 cetacean sighting records with species, group size,
    and observation conditions for marine biodiversity analysis.
    """
    rng = np.random.default_rng(seed=42)
    n = 20
    lats = 46.0 + rng.uniform(0, 3, n)
    lngs = -125.5 + rng.uniform(0, 2, n)
    species = (
        ["Megaptera novaeangliae"] * 8
        + ["Orcinus orca"] * 6
        + ["Eschrichtius robustus"] * 6
    )

    return gpd.GeoDataFrame(
        {
            "sighting_id": [f"SIG_{i:04d}" for i in range(n)],
            "species": species,
            "group_size": rng.integers(1, 12, n),
            "date": pd.date_range("2024-03-01", periods=n, freq="7D").strftime(
                "%Y-%m-%d"
            ),
        },
        geometry=[Point(lng, lat) for lat, lng in zip(lats, lngs)],
        crs="EPSG:4326",
    )
