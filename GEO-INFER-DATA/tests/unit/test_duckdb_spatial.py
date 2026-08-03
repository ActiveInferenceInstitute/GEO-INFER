"""Tests for the cloud-native vector reader with DuckDB-Spatial fallback."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pytest
import shapely

from geo_infer_data.utils.duckdb_spatial import (
    HAS_DUCKDB,
    duckdb_status,
    read_cloud_native_vector,
)


@pytest.fixture
def geojson_file(tmp_path: Path) -> Path:
    """A tiny GeoJSON feature collection on disk."""
    gdf = gpd.GeoDataFrame(
        {"name": ["a", "b"]},
        geometry=[shapely.Point(0, 0), shapely.Point(1, 1)],
        crs="EPSG:4326",
    )
    path = tmp_path / "points.geojson"
    gdf.to_file(path, driver="GeoJSON")
    return path


def test_read_cloud_native_vector_fallback(geojson_file: Path) -> None:
    """Reads a GeoJSON file via the fallback path regardless of duckdb."""
    gdf = read_cloud_native_vector(geojson_file)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert len(gdf) == 2
    assert list(gdf.columns) == ["name", "geometry"]


def test_read_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_cloud_native_vector(tmp_path / "nope.geojson")


def test_duckdb_status_reports_availability() -> None:
    status = duckdb_status()
    if HAS_DUCKDB:
        assert "available" in status
    else:
        assert "fallback" in status


def test_has_duckdb_is_boolean() -> None:
    assert isinstance(HAS_DUCKDB, bool)


def test_read_layer_arg(tmp_path: Path) -> None:
    """The fallback path forwards the layer kwarg without error for GeoJSON."""
    gdf = gpd.GeoDataFrame(
        {"x": [1]}, geometry=[shapely.Point(0, 0)], crs="EPSG:4326"
    )
    path = tmp_path / "single.geojson"
    gdf.to_file(path, driver="GeoJSON")
    # layer=None is safe on the fallback path.
    out = read_cloud_native_vector(path, layer=None)
    assert len(out) == 1
