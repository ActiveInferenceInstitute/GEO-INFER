"""Offline replay and real renderer checks for captured authoritative USGS layers."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import pytest
from shapely.geometry import MultiPolygon, box, mapping, shape

from geo_infer_place.core.regional_layers import (
    BOUNDS,
    TECTONIC_BOUNDS,
    MAX_BYTES,
    SOURCES,
    acquire_regional_layers,
    normalize_regional_layer,
)
from geo_infer_place.core.bioregion_visualization import (
    _load_json,
    create_bioregion_map,
)

CONFIG = Path(__file__).resolve().parents[2] / "locations/cascadia/config"


def test_captured_sources_rebuild_exact_layer_bytes(tmp_path):
    receipt = json.loads((CONFIG / "cascadia_layers.provenance.json").read_text())
    total = 0
    for kind, spec in SOURCES.items():
        raw = (CONFIG / spec["raw"]).read_bytes()
        total += len(raw) + (CONFIG / spec["output"]).stat().st_size
        assert (
            hashlib.sha256(raw).hexdigest() == receipt["layers"][kind]["source_sha256"]
        )
        shutil.copy2(CONFIG / spec["raw"], tmp_path / spec["raw"])
    assert total < MAX_BYTES
    rebuilt = acquire_regional_layers(tmp_path, offline=True)
    for kind, spec in SOURCES.items():
        assert (tmp_path / spec["output"]).read_bytes() == (
            CONFIG / spec["output"]
        ).read_bytes()
        assert (
            rebuilt["layers"][kind]["output_sha256"]
            == receipt["layers"][kind]["output_sha256"]
        )


@pytest.mark.parametrize("kind", list(SOURCES))
def test_real_geometry_ids_bounds_and_renderer_loader(kind):
    spec = SOURCES[kind]
    data = json.loads((CONFIG / spec["output"]).read_text())
    loaded = _load_json(CONFIG / spec["output"])
    assert len(loaded["features"]) == len(data["features"])
    ids = [f["id"] for f in data["features"]]
    assert len(set(ids)) == len(ids) > 0
    window = box(*(TECTONIC_BOUNDS if kind == "tectonics" else BOUNDS))
    for feature in data["features"]:
        geometry = shape(feature["geometry"])
        assert geometry.is_valid and not geometry.is_empty
        assert window.covers(geometry)
    assert not data["provenance"]["whole_cascadia_bioregion"]


def test_real_renderer_reports_only_missing_bioregion_boundary(tmp_path):
    output = tmp_path / "regional.html"
    create_bioregion_map(CONFIG, {}, output, allow_missing_layers=True)
    html = output.read_text()
    assert "Cascadia Subduction Zone" in html and "Major Watersheds" in html
    assert "Mount St. Helens" in html and "Willamette" in html
    assert "Unavailable layers: cascadia_bioregion_boundary.geojson" in html
    manifest = json.loads(output.with_suffix(".layers.json").read_text())
    assert manifest["status"] == "partial"
    assert sum(item["status"] == "loaded" for item in manifest["layers"].values()) == 3
    assert "37%" not in html


def test_whole_bioregion_boundary_remains_fail_closed(tmp_path):
    assert not (CONFIG / "cascadia_bioregion_boundary.geojson").exists()
    with pytest.raises(FileNotFoundError, match="cascadia_bioregion_boundary"):
        create_bioregion_map(CONFIG, {}, tmp_path / "strict.html")


def test_tectonic_original_metadata_has_no_access_or_use_restrictions():
    metadata = json.loads(
        (CONFIG / "cascadia_regional_source_metadata.json").read_text()
    )["tectonics"]
    raw = (CONFIG / metadata["metadata_file"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == metadata["metadata_sha256"]
    root = ET.fromstring(raw)
    assert {node.text.strip().lower() for node in root.iter("useconst")} == {"none"}
    assert {node.text.strip().lower() for node in root.iter("accconst")} == {"none"}


@pytest.mark.parametrize(
    "case", ["duplicate_id", "truncated", "bad_crs", "bad_geometry", "oversized_count"]
)
def test_invalid_source_cannot_generate_layer(case):
    data = json.loads((CONFIG / SOURCES["watersheds"]["raw"]).read_text())
    if case == "duplicate_id":
        data["features"].append(deepcopy(data["features"][0]))
    elif case == "truncated":
        data["exceededTransferLimit"] = True
    elif case == "bad_crs":
        data["crs"] = dict(type="name", properties=dict(name="EPSG:3857"))
    elif case == "bad_geometry":
        data["features"][0]["geometry"] = dict(type="Point", coordinates=[0, 0])
    elif case == "oversized_count":
        data["features"] = [data["features"][0]] * 1001
    with pytest.raises(ValueError):
        normalize_regional_layer("watersheds", json.dumps(data).encode())


def test_duplicate_json_keys_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        normalize_regional_layer(
            "volcanoes", b'{"type":"a","type":"FeatureCollection"}'
        )


def test_watershed_boundary_contact_does_not_become_a_line():
    data = json.loads((CONFIG / SOURCES["watersheds"]["raw"]).read_text())
    contact = deepcopy(data["features"][0])
    contact["properties"]["huc4"] = "1799"
    contact["geometry"] = mapping(box(BOUNDS[2], 41, BOUNDS[2] + 1, 42))
    original = normalize_regional_layer("watersheds", json.dumps(data).encode())
    data["features"].append(contact)
    result = normalize_regional_layer("watersheds", json.dumps(data).encode())
    assert [f["id"] for f in result["features"]] == [
        f["id"] for f in original["features"]
    ]
    assert all(
        f["geometry"]["type"] in {"Polygon", "MultiPolygon"} for f in result["features"]
    )


def test_tectonic_endpoint_contact_does_not_become_a_point():
    feature = dict(
        type="Feature",
        properties={
            "Type": "Convergent",
            "Name": "North America:Juan de Fuca",
            "OBJECTID": 1,
        },
        geometry={"type": "LineString", "coordinates": [[-131, 39], [-130, 40]]},
    )
    raw = json.dumps(dict(type="FeatureCollection", features=[feature])).encode()
    with pytest.raises(ValueError, match="No source features"):
        normalize_regional_layer("tectonics", raw)


def test_mixed_clipped_geometry_collection_is_rejected():
    data = json.loads((CONFIG / SOURCES["watersheds"]["raw"]).read_text())
    feature = deepcopy(data["features"][0])
    feature["geometry"] = mapping(
        MultiPolygon([box(-120, 42, -119, 43), box(BOUNDS[2], 41, BOUNDS[2] + 1, 42)])
    )
    data["features"] = [feature]
    with pytest.raises(ValueError, match="retain its source geometry type"):
        normalize_regional_layer("watersheds", json.dumps(data).encode())


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity", "1e309"])
def test_nonfinite_json_numbers_rejected_before_geometry(token):
    raw = ('{"type":"FeatureCollection","features":[],"number":' + token + "}").encode()
    with pytest.raises(ValueError, match="finite|Nonfinite"):
        normalize_regional_layer("watersheds", raw)


@pytest.mark.parametrize(
    "case", ["before", "headers", "stream_end", "chunk", "bytes", "redirect", "success"]
)
def test_download_bounds_are_enforced_at_cooperative_checkpoints(monkeypatch, case):
    from geo_infer_place.core import _regional_download_worker as module

    clock = [0.0]
    calls = []
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])

    class Response:
        is_redirect = case == "redirect"
        status_code = 302 if is_redirect else 200

        def __enter__(self):
            if case == "headers":
                clock[0] = 2
            return self

        def __exit__(self, *args):
            return False

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size):
            assert chunk_size == 64 * 1024
            if case == "chunk":
                clock[0] = 2
            yield b"ok"
            if case == "stream_end":
                clock[0] = 2

    def get(url, **options):
        calls.append(options)
        return Response()

    monkeypatch.setattr(module.requests, "get", get)
    if case == "before":
        clock[0] = 2
    if case in {"before", "headers", "stream_end", "chunk"}:
        with pytest.raises(TimeoutError, match="cooperative deadline"):
            module._fetch_bytes(
                "https://example.test/source", deadline=1, remaining_bytes=2
            )
    elif case in {"bytes", "redirect"}:
        with pytest.raises(ValueError):
            module._fetch_bytes(
                "https://example.test/source", deadline=1, remaining_bytes=1
            )
    else:
        assert (
            module._fetch_bytes(
                "https://example.test/source", deadline=1, remaining_bytes=2
            )
            == b"ok"
        )
    if case == "before":
        assert calls == []
    else:
        assert calls[0] == {
            "stream": True,
            "timeout": (1.0, 1.0),
            "allow_redirects": False,
        }
