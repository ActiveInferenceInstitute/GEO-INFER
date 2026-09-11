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
    gdf = gpd.GeoDataFrame({"x": [1]}, geometry=[shapely.Point(0, 0)], crs="EPSG:4326")
    path = tmp_path / "single.geojson"
    gdf.to_file(path, driver="GeoJSON")
    # layer=None is safe on the fallback path.
    out = read_cloud_native_vector(path, layer=None)
    assert len(out) == 1


def test_read_quote_containing_path(tmp_path: Path) -> None:
    """A path containing a single quote must round-trip, not inject SQL."""
    gdf = gpd.GeoDataFrame(
        {"name": ["it's"]},
        geometry=[shapely.Point(2, 2)],
        crs="EPSG:4326",
    )
    tricky_dir = tmp_path / "bob's files"
    tricky_dir.mkdir()
    path = tricky_dir / "quote's test.geojson"
    gdf.to_file(path, driver="GeoJSON")
    out = read_cloud_native_vector(path)
    assert isinstance(out, gpd.GeoDataFrame)
    assert len(out) == 1
    assert out["name"].tolist() == ["it's"]


def test_read_directory_raises(tmp_path: Path) -> None:
    """A path that exists but is not a regular file is rejected."""
    with pytest.raises(FileNotFoundError, match="Not a regular file"):
        read_cloud_native_vector(tmp_path)


@pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb-spatial not installed")
def test_duckdb_and_fallback_agree_on_projected_crs(tmp_path: Path) -> None:
    """GS-109: the DuckDB fast path must preserve the file's CRS, not
    hardcode EPSG:4326. A projected (EPSG:32610) FlatGeobuf must yield the
    identical CRS through both engines."""
    gdf = gpd.GeoDataFrame(
        {"name": ["a", "b"]},
        geometry=[
            shapely.Point(500000, 4649776),
            shapely.Point(500100, 4649800),
        ],
        crs="EPSG:32610",
    )
    path = tmp_path / "projected.fgb"
    gdf.to_file(path, driver="FlatGeobuf")

    fast = read_cloud_native_vector(path, use_duckdb=True)
    slow = read_cloud_native_vector(path, use_duckdb=False)

    assert fast.crs == slow.crs
    assert fast.crs is not None and fast.crs.to_epsg() == 32610
    assert fast["name"].tolist() == slow["name"].tolist()
    assert fast.geometry.iloc[0].x == slow.geometry.iloc[0].x


@pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb-spatial not installed")
def test_duckdb_fast_path_reports_wgs84_for_wgs84_file(tmp_path: Path) -> None:
    """A WGS84 GeoParquet still resolves to EPSG:4326 via spec-default metadata."""
    gdf = gpd.GeoDataFrame(
        {"name": ["x"]}, geometry=[shapely.Point(1, 2)], crs="EPSG:4326"
    )
    path = tmp_path / "wgs.parquet"
    gdf.to_parquet(path)

    from geo_infer_data.utils.duckdb_spatial import _resolve_crs
    import duckdb as _duckdb

    conn = _duckdb.connect()
    try:
        conn.execute("INSTALL spatial; LOAD spatial;")
        crs = _resolve_crs(conn, path.as_posix())
    finally:
        conn.close()
    assert crs is not None and crs.to_epsg() == 4326
