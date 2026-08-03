"""Tests for the GeoLibre .geolibre.json project writer (item 2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geo_infer_space.core.geolibre_projects import (
    DEFAULT_BASEMAP_STYLE_URL,
    DEFAULT_LAYER_STYLE,
    GEOLIBRE_PROJECT_VERSION,
    build_h3_grid_project,
    build_project,
    default_map_view,
    dumps_project,
    geojson_layer,
    tile_layer,
    write_project,
)


def sample_feature_collection() -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"h3": "8928308280fffff"},
                "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
            }
        ],
    }


def test_default_map_view() -> None:
    view = default_map_view()
    assert view["center"] == [-100, 40]
    assert view["zoom"] == 2


def test_default_map_view_custom() -> None:
    view = default_map_view(center=[-122.4, 37.7], zoom=10)
    assert view["center"] == [-122.4, 37.7]
    assert view["zoom"] == 10.0


def test_default_map_view_bad_center() -> None:
    with pytest.raises(ValueError):
        default_map_view(center=[1, 2, 3])


def test_geojson_layer_structure() -> None:
    layer = geojson_layer("grid", sample_feature_collection(), fillColor="#ff0000")
    assert layer["type"] == "geojson"
    assert layer["id"] == "layer-0"
    assert layer["name"] == "grid"
    assert layer["visible"] is True
    assert layer["geojson"] == sample_feature_collection()
    assert layer["style"]["fillColor"] == "#ff0000"
    assert layer["source"]["type"] == "geojson"


def test_geojson_layer_explicit_id() -> None:
    layer = geojson_layer("grid", sample_feature_collection(), layer_id="my-layer", index=7)
    assert layer["id"] == "my-layer"


def test_geojson_layer_style_not_shared_between_layers() -> None:
    a = geojson_layer("a", sample_feature_collection(), fillColor="#aa0000")
    b = geojson_layer("b", sample_feature_collection())
    # Mutating one layer's nested style must not affect the other.
    a["style"]["vectorStyleStops"][0]["color"] = "#000000"
    assert b["style"]["vectorStyleStops"][0]["color"] == "#dbeafe"


def test_tile_layer() -> None:
    layer = tile_layer("tiles", "https://example.com/{z}/{x}/{y}.png", attribution="OSM")
    assert layer["type"] == "xyz"
    assert layer["source"]["type"] == "raster"
    assert layer["source"]["tiles"] == ["https://example.com/{z}/{x}/{y}.png"]
    assert layer["source"]["attribution"] == "OSM"
    assert layer["metadata"]["sourceKind"] == "xyz-url"


def test_build_project_top_level() -> None:
    project = build_project(
        "Demo",
        [geojson_layer("grid", sample_feature_collection())],
        center=[10, 20],
        zoom=5,
        metadata={"source": "geo-infer"},
    )
    assert project["version"] == GEOLIBRE_PROJECT_VERSION
    assert project["name"] == "Demo"
    assert project["mapView"]["center"] == [10, 20]
    assert project["mapView"]["zoom"] == 5.0
    assert project["basemapStyleUrl"] == DEFAULT_BASEMAP_STYLE_URL
    assert project["basemapVisible"] is True
    assert project["basemapOpacity"] == 1
    assert len(project["layers"]) == 1
    assert project["styles"] == {}
    assert project["metadata"]["source"] == "geo-infer"


def test_build_project_preferences_copied_per_call() -> None:
    p1 = build_project("A", [])
    p2 = build_project("B", [])
    p1["preferences"]["map"]["restrictBounds"] = True
    assert p2["preferences"]["map"]["restrictBounds"] is False


def test_dumps_project_stable() -> None:
    project = build_project("Demo", [geojson_layer("g", sample_feature_collection())])
    s1 = dumps_project(project)
    s2 = dumps_project(build_project("Demo", [geojson_layer("g", sample_feature_collection())]))
    assert s1 == s2
    # Round-trips to identical dict.
    assert json.loads(s1) == json.loads(s2)


def test_write_project(tmp_path: Path) -> None:
    project = build_project("Demo", [])
    out = write_project(project, tmp_path / "demo" / "project.geolibre.json")
    assert out.exists()
    assert out.suffix == ".json"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["name"] == "Demo"
    assert data["version"] == GEOLIBRE_PROJECT_VERSION


def test_build_h3_grid_project() -> None:
    project = build_h3_grid_project("H3 demo", sample_feature_collection())
    assert project["name"] == "H3 demo"
    layer = project["layers"][0]
    assert layer["type"] == "geojson"
    assert layer["style"]["fillColor"] == "#3b82f6"
    assert layer["style"]["fillOpacity"] == 0.4
    assert layer["geojson"]["features"][0]["properties"]["h3"] == "8928308280fffff"


def test_default_layer_style_present() -> None:
    assert DEFAULT_LAYER_STYLE["minZoom"] == 0
    assert DEFAULT_LAYER_STYLE["maxZoom"] == 24
    assert "fillColor" in DEFAULT_LAYER_STYLE
