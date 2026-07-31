"""Tests for the configurable GeoJSON path seam in UnifiedH3Backend.

DOMAIN-02 / review scoping: the backend previously hard-coded the CWD-relative
path ``config/target_areas.geojson``.  Callers can now pass an explicit
``geojson_path``; the hard-coded default is retained for compatibility.  These
tests pin the new seam and the missing-file behavior without touching the
working directory.
"""

import json

from pathlib import Path

from geo_infer_space.core.unified_backend import UnifiedH3Backend


def _write_target_areas_geojson(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"area": "TestRegion", "subarea": "all"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]],
                },
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _backend(tmp_path: Path, **kwargs) -> UnifiedH3Backend:
    return UnifiedH3Backend(modules={}, resolution=8, **kwargs)


def test_geojson_path_parameter_is_used(tmp_path):
    """Explicit geojson_path is honored instead of the CWD-relative default."""
    geojson = _write_target_areas_geojson(tmp_path / "inputs" / "areas.geojson")
    backend = _backend(tmp_path, geojson_path=geojson)
    assert backend.geojson_path == geojson
    geometries = backend._get_geometries({"TestRegion": ["all"]})
    assert "TestRegion" in geometries
    assert "all" in geometries["TestRegion"]


def test_default_geojson_path_kept_for_compatibility(tmp_path):
    """Legacy default path is preserved when no explicit path is given."""
    backend = _backend(tmp_path)
    assert backend.geojson_path == Path("config/target_areas.geojson")


def test_missing_geojson_returns_empty_without_raising(tmp_path):
    """A missing GeoJSON file yields an empty geometry dict, not an exception."""
    backend = _backend(tmp_path, geojson_path=tmp_path / "does-not-exist.geojson")
    assert backend._get_geometries({"TestRegion": ["all"]}) == {}