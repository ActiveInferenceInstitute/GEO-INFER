"""Unit tests for the NormativeAPI FastAPI routes."""

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_norms.api.normative_api import NormativeAPI


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(NormativeAPI().router)
    return TestClient(app)


def _norm_payload(**overrides):
    payload = {
        "name": "Recycling norm",
        "description": "Households separate recyclables",
        "category": "environmental",
        "strength": 0.7,
        "jurisdiction_ids": ["jur-a", "jur-b"],
        "factors": {"visibility": 0.8, "sanction": 0.5},
        "related_policies": ["pol-1"],
        "tags": ["waste"],
    }
    payload.update(overrides)
    return payload


def test_create_get_list_norms(client):
    created = client.post("/norms", json=_norm_payload())
    assert created.status_code == 200
    norm_id = created.json()["norm_id"]

    got = client.get(f"/norms/{norm_id}").json()
    assert got["name"] == "Recycling norm"
    assert got["strength"] == 0.7

    listed = client.get("/norms").json()
    assert any(n["id"] == norm_id for n in listed)

    missing = client.get("/norms/ghost")
    assert missing.status_code == 404


def test_create_norm_registers_diffusion_entities(client):
    created = client.post("/norms", json=_norm_payload())
    assert created.status_code == 200
    norm_id = created.json()["norm_id"]

    # The diffusion engine knows the submitted jurisdictions after creation,
    # so the simulation endpoint operates on the same entity set.
    response = client.post(
        "/diffusion/simulate",
        json={
            "norm_id": norm_id,
            "time_steps": 5,
            "initial_conditions": {"seed_jurisdictions": ["jur-a"]},
            "parameters": {"threshold": 0.5},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["time_steps"] == 5
    assert len(body["time_series"]) >= 1
    assert len(body["jurisdictions"]) == 2


def test_export_geojson_without_geometry(client):
    client.post(
        "/norms",
        json=_norm_payload(name="Filtered norm", category="social", strength=0.4),
    )

    # Norms created through the API carry no spatial geometry, so the
    # export succeeds but emits no features.
    response = client.get("/export/geojson")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["feature_count"] == 0
    assert body["geojson"]["type"] == "FeatureCollection"

    by_category = client.get(
        "/export/geojson", params={"category": "social"}
    ).json()
    assert by_category["feature_count"] == 0

    below = client.get(
        "/export/geojson", params={"min_strength": 0.9}
    ).json()
    assert below["feature_count"] == 0


def test_diffusion_factors(client):
    norm_id = client.post("/norms", json=_norm_payload()).json()["norm_id"]
    response = client.get(f"/diffusion/factors/{norm_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["norm_id"] == norm_id
    assert body["factors"]["visibility"]["importance"] == 0.8
    assert body["overall_diffusion_potential"] == pytest.approx(0.65)


def test_diffusion_factors_missing_norm(client):
    response = client.get("/diffusion/factors/ghost")
    assert response.status_code == 404


def test_simulate_norm_diffusion(client):
    norm_id = client.post("/norms", json=_norm_payload()).json()["norm_id"]
    response = client.post(
        "/diffusion/simulate",
        json={
            "norm_id": norm_id,
            "time_steps": 5,
            "initial_conditions": {"seed_jurisdictions": ["jur-a"]},
            "parameters": {"threshold": 0.5},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["time_steps"] == 5
    assert len(body["time_series"]) >= 1
    assert len(body["jurisdictions"]) == 2


def test_simulate_norm_diffusion_unknown_norm(client):
    response = client.post(
        "/diffusion/simulate", json={"norm_id": "ghost", "time_steps": 3}
    )
    assert response.status_code == 404


def test_perform_normative_inference_csv(client, tmp_path):
    csv_path = tmp_path / "observations.csv"
    csv_path.write_text(
        "entity_id,recycling,value\nent-1,yes,1\nent-2,no,0\nent-3,yes,1\n",
        encoding="utf-8",
    )
    response = client.post(
        "/inference/analyze",
        json={
            "data_source": str(csv_path),
            "inference_type": "behavioral",
            "parameters": {
                "behavior": "recycling",
                "expected_value": "yes",
                "norm_name": "Recycling compliance",
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["inferred_norms"]) == 3
    assert body["inferred_norms"][0]["compliance_probability"] > 0.5


def test_perform_normative_inference_geojson(client, tmp_path):
    geojson_path = tmp_path / "sites.geojson"
    geojson_path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"entity_id": "ent-1", "permit": True},
                        "geometry": None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    response = client.post(
        "/inference/analyze",
        json={
            "data_source": str(geojson_path),
            "inference_type": "permitting",
            "parameters": {"behavior": "permit"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["inferred_norms"]) == 1
    assert body["inferred_norms"][0]["compliance_probability"] == 1.0


def test_perform_normative_inference_missing_source(client):
    response = client.post(
        "/inference/analyze",
        json={"data_source": "/nonexistent/path/data.csv", "inference_type": "x"},
    )
    assert response.status_code == 404


def test_perform_normative_inference_bad_extension(client, tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("hello", encoding="utf-8")
    response = client.post(
        "/inference/analyze",
        json={"data_source": str(path), "inference_type": "x"},
    )
    assert response.status_code == 415


def test_perform_normative_inference_missing_value_field(client, tmp_path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("entity_id,other\nent-1,1\n", encoding="utf-8")
    response = client.post(
        "/inference/analyze",
        json={
            "data_source": str(csv_path),
            "inference_type": "x",
            "parameters": {"behavior": "missing_field"},
        },
    )
    assert response.status_code == 422


def test_analyze_spatial_patterns(client, tmp_path):
    csv_path = tmp_path / "locations.csv"
    csv_path.write_text(
        "entity_id,compliance,lon,lat\nent-1,yes,-122.3,47.6\nent-2,yes,-122.31,47.61\n",
        encoding="utf-8",
    )
    seeded = client.post(
        "/inference/analyze",
        json={
            "data_source": str(csv_path),
            "inference_type": "behavioral",
            "parameters": {"behavior": "compliance", "expected_value": "yes"},
        },
    )
    assert seeded.status_code == 200

    response = client.post(
        "/inference/spatial-patterns",
        json={
            "data_source": str(csv_path),
            "inference_type": "behavioral",
            "spatial_extent": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-122.5, 47.4],
                        [-122.2, 47.4],
                        [-122.2, 47.7],
                        [-122.5, 47.7],
                        [-122.5, 47.4],
                    ]
                ],
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"


def test_assess_policy_impact(client):
    norm_id = client.post("/norms", json=_norm_payload()).json()["norm_id"]
    response = client.post(
        "/policy-impact",
        json={
            "norm_id": norm_id,
            "policy_id": "pol-1",
            "time_horizon": 24,
            "parameters": {
                "policy_effectiveness": 0.8,
                "public_awareness": 0.6,
                "enforcement_level": 0.4,
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["final_strength"] >= body["initial_strength"]
    assert body["key_factors"]["combined_effect"] == pytest.approx(0.6)
    assert len(body["impact_projections"]) >= 2


def test_assess_policy_impact_unknown_norm(client):
    response = client.post(
        "/policy-impact",
        json={"norm_id": "ghost", "policy_id": "pol-1", "time_horizon": 12},
    )
    assert response.status_code == 404


def test_get_norms_at_point_requires_spatial_geometry(client):
    client.post("/norms", json=_norm_payload(name="Pointless norm"))

    # Without spatial geometry a norm is never contained by any point.
    hits = client.post(
        "/spatial/norms-at-point", json={"lat": 47.61, "lon": -122.33}
    ).json()
    assert hits == []
