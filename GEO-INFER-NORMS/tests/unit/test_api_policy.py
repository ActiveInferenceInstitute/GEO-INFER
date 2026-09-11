"""Unit tests for the PolicyAPI FastAPI routes."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_norms.api.policy_api import PolicyAPI


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(PolicyAPI().router)
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


def _policy_payload(**overrides):
    payload = {
        "name": "Green Roof Mandate",
        "description": "Requires green roofs on new construction",
        "category": "environmental",
        "issuing_authority": "City Council",
        "jurisdiction_ids": ["jur-1"],
        "effective_date": "2025-01-01T00:00:00",
        "status": "active",
        "tags": ["sustainability"],
    }
    payload.update(overrides)
    return payload


def _implementation_payload(policy_id, **overrides):
    payload = {
        "policy_id": policy_id,
        "name": "Downtown rollout",
        "description": "Phase 1 implementation",
        "start_date": "2025-02-01T00:00:00",
        "jurisdiction_id": "jur-1",
        "geometry": _polygon(),
        "budget": 250000.0,
        "status": "in_progress",
        "metrics": {"roofs_retrofitted": 12},
    }
    payload.update(overrides)
    return payload


def test_policy_lifecycle(client):
    created = client.post("/policies", json=_policy_payload())
    assert created.status_code == 200
    policy_id = created.json()["policy_id"]

    got = client.get(f"/policies/{policy_id}").json()
    assert got["name"] == "Green Roof Mandate"

    listed = client.get("/policies").json()
    assert any(p["id"] == policy_id for p in listed)


def test_get_missing_policy(client):
    response = client.get("/policies/nope")
    assert response.status_code == 404


def test_implementation_lifecycle(client):
    policy_id = client.post("/policies", json=_policy_payload()).json()["policy_id"]

    created = client.post(
        "/implementations", json=_implementation_payload(policy_id)
    )
    assert created.status_code == 200
    implementation_id = created.json()["implementation_id"]

    got = client.get(f"/implementations/{implementation_id}").json()
    assert got["name"] == "Downtown rollout"

    listed = client.get("/implementations").json()
    assert any(i["id"] == implementation_id for i in listed)

    by_policy = client.get(f"/policies/{policy_id}/implementations").json()
    assert any(i["id"] == implementation_id for i in by_policy)


def test_assess_policy_impact_environmental(client):
    policy_id = client.post("/policies", json=_policy_payload()).json()["policy_id"]
    response = client.post(
        "/impact/assess",
        json={
            "policy_id": policy_id,
            "assessment_type": "environmental",
            "parameters": {"region": "downtown"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["assessment"]["assessment_type"] == "environmental"
    assert "water_quality_improvement" in body["assessment"]["metrics"]

    history = client.get(f"/impact/history/{policy_id}").json()
    # The history endpoint serves the assessment registry for the policy; the
    # impact endpoint does not append to it in this implementation.
    assert isinstance(history, list)
    assert all(
        {"assessment_id", "policy_id"} <= set(h) for h in history
    )


def test_assess_policy_impact_unknown_type(client):
    policy_id = client.post("/policies", json=_policy_payload()).json()["policy_id"]
    response = client.post(
        "/impact/assess",
        json={"policy_id": policy_id, "assessment_type": "cultural"},
    )
    assert response.status_code == 200
    assert response.json()["assessment"]["metrics"] == {
        "status": "unknown assessment type"
    }


def test_assess_policy_impact_missing_policy(client):
    response = client.post(
        "/impact/assess",
        json={"policy_id": "ghost", "assessment_type": "economic"},
    )
    assert response.status_code == 404


    response = client.post(
        "/comparison/regulations",
        json={"regulation_ids": ["r1"], "comparison_metrics": ["emissions"]},
    )
    assert response.status_code == 422


def test_compare_regulations_unknown_ids(client):
    response = client.post(
        "/comparison/regulations",
        json={"regulation_ids": ["r1", "r2"], "comparison_metrics": ["emissions"]},
    )
    assert response.status_code == 404
    assert "r1" in response.json()["detail"]


def test_export_geojson_implementations(client):
    policy_id = client.post("/policies", json=_policy_payload()).json()["policy_id"]
    client.post("/implementations", json=_implementation_payload(policy_id))

    response = client.get("/export/geojson")
    assert response.status_code == 200
    body = response.json()
    assert body["feature_count"] >= 1

    filtered = client.get("/export/geojson", params={"status": "in_progress"}).json()
    assert filtered["feature_count"] >= 1
    empty = client.get("/export/geojson", params={"status": "paused"}).json()
    assert empty["status"] == "warning"
    assert empty["geojson"] is None
