"""
Tests for the processing algorithm registry endpoints.

These tests verify the /api/v1/algorithms surface: listing, describing, and
running registered algorithms through the FastAPI app. They exercise both
branches of the graceful import: when GEO-INFER-SPACE is importable the
endpoints serve the reference registry, and when it is not they report the
service as unavailable (HTTP 503) instead of failing at import time.
"""

from fastapi.testclient import TestClient

from geo_infer_api.app import main_app
from geo_infer_api.endpoints.algorithms_router import (
    HAS_ALGORITHM_REGISTRY,
)

client = TestClient(main_app)

GRID_LAYER = {
    "id": "grid",
    "geojson": {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {}, "geometry": None}],
    },
}


def test_list_algorithms() -> None:
    resp = client.get("/api/v1/algorithms")
    if not HAS_ALGORITHM_REGISTRY:
        assert resp.status_code == 503
        return
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] >= 2
    ids = {a["id"] for a in body["algorithms"]}
    assert {"calculate-bounds", "count-features"} <= ids


def test_list_algorithms_shape() -> None:
    resp = client.get("/api/v1/algorithms")
    if not HAS_ALGORITHM_REGISTRY:
        return
    algorithm = resp.json()["algorithms"][0]
    for key in ("id", "name", "description", "parameters"):
        assert key in algorithm


def test_get_algorithm() -> None:
    resp = client.get("/api/v1/algorithms/count-features")
    if not HAS_ALGORITHM_REGISTRY:
        assert resp.status_code == 503
        return
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "count-features"
    assert body["parameters"][0]["id"] == "layer"
    assert body["parameters"][0]["required"] is True


def test_get_unknown_algorithm_404() -> None:
    resp = client.get("/api/v1/algorithms/does-not-exist")
    if not HAS_ALGORITHM_REGISTRY:
        assert resp.status_code == 503
        return
    assert resp.status_code == 404


def test_run_count_features() -> None:
    payload = {"layers": [GRID_LAYER], "parameters": {"layer": "grid"}}
    resp = client.post("/api/v1/algorithms/count-features/run", json=payload)
    if not HAS_ALGORITHM_REGISTRY:
        assert resp.status_code == 503
        return
    assert resp.status_code == 200
    body = resp.json()
    assert body["algorithm_id"] == "count-features"
    assert body["result"] == 1
    assert body["logs"] == ["Feature count: 1"]


def test_run_unknown_algorithm_404() -> None:
    resp = client.post(
        "/api/v1/algorithms/nope/run",
        json={"layers": [], "parameters": {}},
    )
    if not HAS_ALGORITHM_REGISTRY:
        assert resp.status_code == 503
        return
    assert resp.status_code == 404


def test_run_calculate_bounds() -> None:
    payload = {
        "layers": [
            {
                "id": "grid",
                "geojson": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[[0, 0], [2, 0], [2, 1], [0, 1], [0, 0]]],
                            },
                        }
                    ],
                },
            }
        ],
        "parameters": {"layer": "grid"},
    }
    resp = client.post("/api/v1/algorithms/calculate-bounds/run", json=payload)
    if not HAS_ALGORITHM_REGISTRY:
        assert resp.status_code == 503
        return
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == [0.0, 0.0, 2.0, 1.0]
