"""Unit tests for the ZoningAPI FastAPI routes."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_norms.api.zoning_api import ZoningAPI


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(ZoningAPI().router)
    return TestClient(app)


def _polygon():
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-122.4, 47.5],
                [-122.2, 47.5],
                [-122.2, 47.7],
                [-122.4, 47.7],
                [-122.4, 47.5],
            ]
        ],
    }


def _code_payload(**overrides):
    payload = {
        "code": "R1",
        "name": "Single-family residential",
        "description": "Low density housing",
        "category": "residential",
        "allowed_uses": ["single_family"],
        "conditional_uses": ["home_office"],
        "prohibited_uses": ["heavy_industrial"],
        "max_height": 12.0,
        "max_density": 2.5,
        "min_lot_size": 5000.0,
        "max_lot_coverage": 0.4,
    }
    payload.update(overrides)
    return payload


def test_zoning_code_lifecycle(client):
    created = client.post("/codes", json=_code_payload())
    assert created.status_code == 200
    assert created.json()["code"] == "R1"

    got = client.get("/codes/R1").json()
    assert got["name"] == "Single-family residential"

    listed = client.get("/codes").json()
    assert any(c["code"] == "R1" for c in listed)


def test_zoning_district_lifecycle(client):
    client.post("/codes", json=_code_payload())
    created = client.post(
        "/districts",
        json={
            "name": "North Residential",
            "description": "Residential district",
            "zoning_code": "R1",
            "jurisdiction_id": "jur-1",
            "geometry": _polygon(),
        },
    )
    assert created.status_code == 200
    district_id = created.json()["district_id"]

    got = client.get(f"/districts/{district_id}").json()
    assert got["name"] == "North Residential"

    listed = client.get("/districts").json()
    assert any(d["id"] == district_id for d in listed)

    filtered = client.get(
        "/districts", params={"zoning_code": "R1", "with_geometry": True}
    ).json()
    assert filtered
    assert all(d["zoning_code"] == "R1" for d in filtered)
    assert all(d.get("geometry") for d in filtered)

    other = client.get("/districts", params={"zoning_code": "C1"}).json()
    assert other == []


def test_districts_at_point(client):
    client.post("/codes", json=_code_payload())
    client.post(
        "/districts",
        json={
            "name": "Spatial District",
            "zoning_code": "R1",
            "geometry": _polygon(),
        },
    )

    hits = client.post(
        "/analyze/districts-at-point", json={"lat": 47.6, "lon": -122.3}
    ).json()
    assert any(d["name"] == "Spatial District" for d in hits)

    misses = client.post(
        "/analyze/districts-at-point", json={"lat": 5.0, "lon": 5.0}
    ).json()
    assert misses == []


def test_land_use_type_lifecycle(client):
    created = client.post(
        "/land-uses",
        json={
            "name": "Mixed Use",
            "category": "commercial",
            "description": "Retail plus residential",
            "intensity": 0.6,
        },
    )
    assert created.status_code == 200
    use_type_id = created.json()["land_use_type_id"]

    listed = client.get("/land-uses").json()
    assert any(t["id"] == use_type_id for t in listed)


def test_classify_land_use(client):
    features = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"veg_ratio": 0.8, "bldg_ratio": 0.05},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-122.35, 47.6],
                            [-122.34, 47.6],
                            [-122.34, 47.61],
                            [-122.35, 47.61],
                            [-122.35, 47.6],
                        ]
                    ],
                },
            }
        ],
    }
    response = client.post(
        "/classify/land-use",
        json={
            "geojson_features": features,
            "feature_columns": ["veg_ratio", "bldg_ratio"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["feature_count"] == 1
    assert "properties" in body["geojson"]["features"][0]


def test_calculate_compatibility(client):
    response = client.get(
        "/compatibility", params={"code1": "R1", "code2": "C1"}
    )
    assert response.status_code == 200
    assert 0.0 <= response.json() <= 1.0


def test_evaluate_zoning_change(client):
    client.post("/codes", json=_code_payload())
    client.post(
        "/codes",
        json=_code_payload(code="C1", name="Commercial", category="commercial"),
    )
    district_id = client.post(
        "/districts",
        json={
            "name": "Changeable District",
            "zoning_code": "R1",
            "geometry": _polygon(),
        },
    ).json()["district_id"]

    response = client.post(
        "/analyze/zoning-change",
        json={"district_id": district_id, "new_code": "C1"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_analyze_zoning_boundaries(client):
    client.post("/codes", json=_code_payload())
    client.post(
        "/districts",
        json={"name": "Boundary District", "zoning_code": "R1", "geometry": _polygon()},
    )
    response = client.post("/analyze/boundaries")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
