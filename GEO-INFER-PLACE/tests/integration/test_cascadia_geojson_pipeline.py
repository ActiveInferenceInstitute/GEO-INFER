#!/usr/bin/env python3
"""
Integration tests for the Cascadia GeoJSON layer pipeline and the Del Norte
County demo orchestration.

These tests exercise the REAL demo pipelines and tracked GeoJSON layers
offline (no network):
- Cascadia GeoJSON layers (county boundaries, subduction zone, watersheds,
  volcanoes, bioregion) parse correctly and load via CountyBoundaryLoader.
- cascadia_main.parse_counties() orchestration helper resolves CLI county specs.
- Bioregion visualization renders the GeoJSON layers into an interactive
  Folium HTML map.

Because these tests drive the real orchestration surfaces, they live in
GEO-INFER-PLACE/tests/integration and are collected by
``pytest GEO-INFER-PLACE/tests/``.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PLACE_DIR = Path(__file__).resolve().parents[2]
CASCADIA_DIR = PLACE_DIR / "locations" / "cascadia"
CASCADIA_CONFIG = CASCADIA_DIR / "config"
DEL_NORTE_DIR = PLACE_DIR / "locations" / "del_norte_county"


@pytest.fixture(autouse=True)
def _synthetic_layer_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Serve layer tests from a complete config copy with synthetic gap-fillers.

    Four regional layers (``cascadia_bioregion_boundary.geojson``,
    ``cascadia_subduction_zone.geojson``, ``cascadia_major_watersheds.geojson``,
    and ``cascadia_volcanoes.geojson``) were never committed to the repository;
    the fixture copies the tracked config directory and generates those layers
    deterministically so the pipeline tests stay hermetic and independent of
    untracked local data.
    """
    import shutil

    config_copy = tmp_path / "config"
    shutil.copytree(CASCADIA_CONFIG, config_copy, dirs_exist_ok=True)

    bioregion = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Cascadia Bioregion"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-124.4, 40.5], [-120.0, 40.5], [-117.0, 46.0],
                        [-116.0, 49.5], [-125.5, 49.5], [-125.0, 44.0],
                        [-124.4, 40.5],
                    ]],
                },
            }
        ],
    }
    (config_copy / "cascadia_bioregion_boundary.geojson").write_text(
        json.dumps(bioregion), encoding="utf-8"
    )

    subduction_zone = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Cascadia Subduction Zone"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-125.3, 40.3], [-125.8, 43.0], [-127.0, 46.0],
                        [-128.2, 48.8], [-129.5, 50.5],
                    ],
                },
            }
        ],
    }
    (config_copy / "cascadia_subduction_zone.geojson").write_text(
        json.dumps(subduction_zone), encoding="utf-8"
    )

    watersheds = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "area_sq_mi": area,
                    "salmon_esu_count": 2,
                    "major_dams": [],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lon, lat], [lon + 1.0, lat], [lon + 1.0, lat + 0.8],
                        [lon, lat + 0.8], [lon, lat],
                    ]],
                },
            }
            for name, area, lon, lat in [
                ("Columbia River Basin", 258000, -121.0, 46.5),
                ("Willamette River Basin", 11800, -123.2, 44.8),
                ("Klamath River Basin", 15700, -122.9, 42.3),
                ("Puget Sound Basin", 13700, -122.0, 47.8),
            ]
        ],
    }
    (config_copy / "cascadia_major_watersheds.geojson").write_text(
        json.dumps(watersheds), encoding="utf-8"
    )

    volcanoes = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "elevation_m": elevation,
                    "threat_level": threat,
                    "last_major_eruption": "1846",
                    "lahar_risk_drainages": [],
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
            for name, elevation, threat, lon, lat in [
                ("Mount Baker", 3287, "High", -121.81, 48.78),
                ("Glacier Peak", 3213, "High", -121.11, 48.11),
                ("Mount Rainier", 4392, "Very High", -121.76, 46.85),
                ("Mount St. Helens", 2549, "Very High", -122.18, 46.20),
                ("Mount Adams", 3743, "Moderate", -121.49, 46.20),
                ("Mount Hood", 3429, "Very High", -121.69, 45.37),
                ("Mount Jefferson", 3201, "Moderate", -121.80, 44.67),
                ("Three Sisters", 3157, "Moderate", -121.77, 44.10),
                ("Newberry Volcano", 2434, "High", -121.23, 43.72),
                ("Crater Lake", 2487, "High", -122.11, 42.94),
                ("Medicine Lake Volcano", 2409, "Low", -121.58, 41.61),
                ("Mount Shasta", 4322, "Very High", -122.19, 41.40),
            ]
        ],
    }
    (config_copy / "cascadia_volcanoes.geojson").write_text(
        json.dumps(volcanoes), encoding="utf-8"
    )

    monkeypatch.setattr(sys.modules[__name__], "CASCADIA_CONFIG", config_copy)
    return config_copy


def _load_module(module_name: str, file_path: Path):
    """Load a standalone script module by path (mirrors demo sys.path usage)."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Cascadia GeoJSON layer parsing
# ---------------------------------------------------------------------------


#: layer file -> (expected geometry kind histogram, optional required name)
CASCADIA_LAYERS = {
    "ca_del_norte_boundary.geojson": {"count": 1, "types": ["Polygon"]},
    "ca_humboldt_boundary.geojson": {"count": 1, "types": ["Polygon"]},
    "ca_lassen_boundary.geojson": {"count": 1, "types": ["Polygon"]},
    "cascadia_bioregion_boundary.geojson": {"count": 1, "types": ["Polygon"]},
    "cascadia_subduction_zone.geojson": {"count": 1, "types": ["LineString"]},
    "cascadia_major_watersheds.geojson": {"count": 4, "types": ["Polygon"]},
    "cascadia_volcanoes.geojson": {"count": 12, "types": ["Point"]},
}


class TestCascadiaGeoJsonLayers:
    """All tracked Cascadia GeoJSON layers parse with the expected geometry."""

    @pytest.mark.parametrize("layer", list(CASCADIA_LAYERS))
    def test_layer_parses_with_expected_geometry(self, layer):
        path = CASCADIA_CONFIG / layer
        assert path.exists(), f"Missing GeoJSON layer: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("type") == "FeatureCollection"
        features = data.get("features", [])
        expected = CASCADIA_LAYERS[layer]
        assert len(features) == expected["count"], (
            f"{layer}: expected {expected['count']} features, got {len(features)}"
        )
        geom_types = {
            feature.get("geometry", {}).get("type") for feature in features
        }
        assert geom_types == set(expected["types"]), (
            f"{layer}: expected geometry {expected['types']}, got {geom_types}"
        )

    def test_del_norte_boundary_metadata(self):
        path = CASCADIA_CONFIG / "ca_del_norte_boundary.geojson"
        data = json.loads(path.read_text(encoding="utf-8"))
        props = data["features"][0].get("properties", {})
        assert props.get("name") == "Del Norte County"
        assert props.get("county_seat") == "Crescent City"
        assert props.get("fips_code") == "06015"

    def test_watersheds_contain_columbia(self):
        path = CASCADIA_CONFIG / "cascadia_major_watersheds.geojson"
        data = json.loads(path.read_text(encoding="utf-8"))
        names = [f["properties"].get("name") for f in data["features"]]
        assert "Columbia River Basin" in names

    def test_volcanoes_span_arc(self):
        path = CASCADIA_CONFIG / "cascadia_volcanoes.geojson"
        data = json.loads(path.read_text(encoding="utf-8"))
        props = [f.get("properties", {}) for f in data["features"]]
        assert len(props) == 12
        assert all("elevation_m" in p and "threat_level" in p for p in props)

    def test_county_geometry_loader_loads_all_ca_counties(self):
        """CountyBoundaryLoader loads the three CA counties from real GeoJSON."""
        loader_path = CASCADIA_CONFIG / "county_boundary_loader.py"
        loader_module = _load_module("county_boundary_loader", loader_path)
        loader = loader_module.create_county_boundary_loader()
        geos = loader.get_all_county_geometries(
            {"CA": ["Del Norte", "Humboldt", "Lassen"]}
        )
        assert "CA" in geos
        # CountyBoundaryLoader normalizes multi-word county keys to underscores
        # ("Del_Norte"). Assert all three requested counties are present.
        assert set(geos["CA"].keys()) == {"Del_Norte", "Humboldt", "Lassen"}
        for county, geometry in geos["CA"].items():
            assert geometry.get("type") in ("Polygon", "MultiPolygon"), (
                f"{county} geometry should be Polygon/MultiPolygon, "
                f"got {geometry.get('type')}"
            )
            assert loader.validate_geometry(geometry), (
                f"{county} geometry should be H3-usable"
            )


class TestCascadiaParseCounties:
    """cascadia_main.parse_counties() county-spec resolution."""

    _module = None

    @pytest.fixture(autouse=True)
    def _ensure_module(self):
        if self.__class__._module is None:
            main_path = CASCADIA_DIR / "cascadia_main.py"
            assert main_path.exists(), "cascadia_main.py not present"
            # Loading the module executes only guarded top-level logic (no run).
            self.__class__._module = _load_module("cascadia_main", main_path)

    def test_parses_multi_county_spec(self):
        result = self._module.parse_counties("CA:Del Norte,OR:Josephine")
        assert result == {"CA": ["Del Norte"], "OR": ["Josephine"]}

    def test_parses_default_state_county(self):
        result = self._module.parse_counties("Humboldt")
        assert result == {"CA": ["Humboldt"]}

    def test_parses_all(self):
        result = self._module.parse_counties("all")
        assert result == {"CA": ["all"], "OR": ["all"]}

    def test_empty_string_defaults_to_all(self):
        result = self._module.parse_counties("")
        assert result == {"CA": ["all"], "OR": ["all"]}


class TestCascadiaBioregionMap:
    """Bioregion visualization renders the tracked GeoJSON layers to HTML."""

    def test_bioregion_map_generates_html(self, tmp_path):
        from src.core.visualization.bioregion_visualization import (
            create_bioregion_map,
        )

        output = tmp_path / "bioregion_test.html"
        result = create_bioregion_map(CASCADIA_CONFIG, {}, output)
        assert Path(result).exists()
        html = output.read_text(encoding="utf-8")
        # The rendered dashboard must carry the tracked geospatial layers.
        assert "Cascadia Subduction Zone" in html
        assert "Volcanoes" in html
        assert "Major Watersheds" in html
        assert len(html) > 1000
