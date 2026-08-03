"""Cloud-native vector readers with optional DuckDB-Spatial acceleration.

Reads GeoParquet, FlatGeobuf, and Shapefile inputs into GeoDataFrames. When
DuckDB with the Spatial extension is installed, reads route through DuckDB for
fast cloud-native parsing; otherwise the reader transparently falls back to the
always-present GeoPandas/Fiona path. This mirrors the approach GeoLibre uses
for client-side vector import (DuckDB-WASM Spatial) while keeping GEO-INFER's
core importable and testable without the optional dependency.

The fallback keeps behaviour consistent across environments: callers read a
GeoDataFrame either way and never need to branch on which engine ran.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Union

import geopandas as gpd

logger = logging.getLogger(__name__)

try:  # pragma: no cover - import probe
    import duckdb as _duckdb  # type: ignore[import-not-found]

    HAS_DUCKDB: bool = True
    _DUCKDB = _duckdb
except ImportError:  # pragma: no cover - exercised when duckdb is missing
    _DUCKDB = None  # type: ignore[assignment]
    HAS_DUCKDB = False


class DuckDBSpatialError(RuntimeError):
    """Raised when an explicit DuckDB-Spatial read fails."""


def _fallback_read_vector(
    file_path: Path,
    layer: Optional[str] = None,
    **kwargs: Any,
) -> gpd.GeoDataFrame:
    """Read a vector file through GeoPandas/Fiona (always available)."""
    if layer:
        return gpd.read_file(str(file_path), layer=layer, **kwargs)
    return gpd.read_file(str(file_path), **kwargs)


def _duckdb_read_vector(
    file_path: Path,
    layer: Optional[str] = None,
    **kwargs: Any,
) -> gpd.GeoDataFrame:
    """Read a cloud-native vector file through DuckDB Spatial.

    GeoParquet and FlatGeobuf are read natively by DuckDB Spatial's ``ST_Read``
    and returned as a GeoDataFrame. ``layer``/extra kwargs are only supported
    by the fallback path.
    """
    del layer, kwargs
    if _DUCKDB is None:  # pragma: no cover - guarded by callers
        raise DuckDBSpatialError("DuckDB is not installed")
    conn = _DUCKDB.connect()
    try:
        conn.execute("INSTALL spatial; LOAD spatial;")
        rel = conn.sql(f"SELECT * FROM ST_Read('{file_path.as_posix()}')")
        df = rel.df()
        geometry = gpd.GeoSeries.from_wkb(df.pop("geom"))
        return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    finally:
        conn.close()


def read_cloud_native_vector(
    file_path: Union[str, Path],
    *,
    use_duckdb: bool = True,
    layer: Optional[str] = None,
    **kwargs: Any,
) -> gpd.GeoDataFrame:
    """Read a GeoParquet / FlatGeobuf / Shapefile into a GeoDataFrame.

    Args:
        file_path: Path to the vector file.
        use_duckdb: When True (default) and DuckDB+Spatial is installed, use
            the DuckDB fast path; otherwise fall back to GeoPandas/Fiona.
        layer: Optional layer name (fallback path only).
        **kwargs: Extra kwargs forwarded to the reader.

    Returns:
        A GeoDataFrame with the file's features.

    Raises:
        FileNotFoundError: If ``file_path`` does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if use_duckdb and HAS_DUCKDB:
        try:
            return _duckdb_read_vector(path, layer=layer, **kwargs)
        except Exception as exc:  # pragma: no cover - engine dependent
            logger.warning("DuckDB-Spatial read failed (%s); falling back", exc)

    return _fallback_read_vector(path, layer=layer, **kwargs)


def duckdb_status() -> str:
    """Return the DuckDB-Spatial availability status for diagnostics."""
    if not HAS_DUCKDB:
        return "duckdb-spatial: unavailable (using GeoPandas/Fiona fallback)"
    try:
        return "duckdb-spatial: available"
    except Exception:  # pragma: no cover - defensive
        return "duckdb-spatial: unknown"


__all__ = [
    "HAS_DUCKDB",
    "DuckDBSpatialError",
    "read_cloud_native_vector",
    "duckdb_status",
]
