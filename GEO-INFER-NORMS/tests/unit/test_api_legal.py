"""Unit tests for the LegalAPI FastAPI routes."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_norms.api.legal_api import LegalAPI


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(LegalAPI().router)
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


def test_create_and_get_jurisdiction(client):
    created = client.post(
        "/jurisdictions",
        json={
            "name": "Test County",
            "level": "county",
            "description": "A county for testing",
            "code": "TC",
            "geometry": _polygon(),
        },
    )
    assert created.status_code == 200
    jurisdiction_id = created.json()["jurisdiction_id"]

    got = client.get(f"/jurisdictions/{jurisdiction_id}").json()
    assert got["name"] == "Test County"
    assert got["level"] == "county"


def test_list_and_find_jurisdictions(client):
    client.post(
        "/jurisdictions",
        json={"name": "Harbor City", "level": "municipal", "code": "HC"},
    )
    client.post(
        "/jurisdictions", json={"name": "Bay County", "level": "county", "code": "BC"}
    )

    listed = client.get("/jurisdictions").json()
    names = {j["name"] for j in listed}
    assert {"Harbor City", "Bay County"} <= names

    matches = client.get(
        "/jurisdictions/by-name/Harbor City", params={"partial_match": True}
    ).json()
    assert any(j["name"] == "Harbor City" for j in matches)


def test_jurisdiction_hierarchy(client):
    parent = client.post(
        "/jurisdictions", json={"name": "Parent State", "level": "state"}
    ).json()["jurisdiction_id"]
    child = client.post(
        "/jurisdictions",
        json={"name": "Child City", "level": "municipal", "parent_id": parent},
    ).json()["jurisdiction_id"]

    hierarchy = client.get(f"/jurisdictions/hierarchy/{child}").json()
    assert hierarchy
    assert any(item["id"] == parent for item in hierarchy)


def test_regulation_lifecycle(client):
    jurisdiction_id = client.post(
        "/jurisdictions", json={"name": "Reg State", "level": "state"}
    ).json()["jurisdiction_id"]

    created = client.post(
        "/regulations",
        json={
            "name": "Clean Water Act",
            "description": "Limits on discharges",
            "code": "CWA-1",
            "category": "environmental",
            "applicable_jurisdictions": [jurisdiction_id],
            "effective_date": "2024-01-01T00:00:00",
            "tags": ["water"],
        },
    )
    assert created.status_code == 200
    regulation_id = created.json()["regulation_id"]

    got = client.get(f"/regulations/{regulation_id}").json()
    assert got["name"] == "Clean Water Act"

    by_jurisdiction = client.get(
        f"/regulations/jurisdiction/{jurisdiction_id}"
    ).json()
    assert any(r["id"] == regulation_id for r in by_jurisdiction)


def test_frameworks(client):
    created = client.post(
        "/frameworks",
        json={
            "name": "Environmental Framework",
            "description": "Framework for env regulations",
            "authority": "EPA",
            "sector": "environment",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["framework"]["name"] == "Environmental Framework"

    # The list endpoint serves a static example registry, not created frameworks.
    listed = client.get("/frameworks").json()
    assert listed
    assert all({"id", "name", "sector"} <= set(f) for f in listed)


def test_jurisdictions_at_point(client):
    client.post(
        "/jurisdictions",
        json={"name": "Spatial County", "level": "county", "geometry": _polygon()},
    )

    hits = client.post(
        "/spatial/jurisdictions-at-point", json={"lat": 47.6, "lon": -122.3}
    ).json()
    assert any(j["name"] == "Spatial County" for j in hits)

    misses = client.post(
        "/spatial/jurisdictions-at-point", json={"lat": 10.0, "lon": 10.0}
    ).json()
    assert misses == []


def test_regulations_at_point(client):
    jurisdiction_id = client.post(
        "/jurisdictions",
        json={"name": "Point State", "level": "state", "geometry": _polygon()},
    ).json()["jurisdiction_id"]
    client.post(
        "/regulations",
        json={
            "name": "Point Rule",
            "category": "zoning",
            "applicable_jurisdictions": [jurisdiction_id],
        },
    )

    hits = client.post(
        "/spatial/regulations-at-point", json={"lat": 47.6, "lon": -122.3}
    ).json()
    assert any(r["name"] == "Point Rule" for r in hits)


def test_export_geojson_with_jurisdictions(client):
    client.post(
        "/jurisdictions",
        json={"name": "Geo County", "level": "county", "geometry": _polygon()},
    )
    response = client.get("/spatial/export")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["feature_count"] >= 1
    assert body["geojson"]["type"] == "FeatureCollection"


def test_export_geojson_empty(client):
    response = client.get("/spatial/export")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "warning"
    assert body["geojson"] is None
