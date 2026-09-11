"""Unit tests for the ComplianceAPI FastAPI routes."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_norms.api.compliance_api import ComplianceAPI


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(ComplianceAPI().router)
    return TestClient(app)


def _status_payload(**overrides):
    payload = {
        "entity_id": "ent-1",
        "regulation_id": "reg-1",
        "is_compliant": True,
        "compliance_level": 0.9,
        "notes": "ok",
        "metric_results": [{"metric_id": "m-1", "value": 10.0}],
    }
    payload.update(overrides)
    return payload


def _metric_payload(**overrides):
    payload = {
        "name": "Emission limit",
        "description": "Annual emissions below threshold",
        "regulation_id": "reg-1",
        "evaluation_type": "threshold",
        "primary_field": "emission_level",
        "required_fields": ["emission_level"],
        "threshold_value": 50.0,
        "comparison": "less_than",
    }
    payload.update(overrides)
    return payload


def test_add_status_and_get_entity_compliance(client):
    response = client.post("/status", json=_status_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["status_id"]

    entity_info = client.get("/status/entity/ent-1").json()
    assert entity_info["entity_id"] == "ent-1"
    assert entity_info["compliance_count"] == 1


def test_get_regulation_compliance(client):
    client.post("/status", json=_status_payload())
    info = client.get("/status/regulation/reg-1").json()
    assert info["regulation_id"] == "reg-1"
    assert info["entity_count"] == 1


def test_add_and_list_metrics(client):
    created = client.post("/metrics", json=_metric_payload()).json()
    assert created["status"] == "success"

    listed = client.get("/metrics").json()
    assert any(m["name"] == "Emission limit" for m in listed)

    filtered = client.get("/metrics", params={"regulation_id": "reg-1"}).json()
    assert filtered
    assert all(m["regulation_id"] == "reg-1" for m in filtered)

    empty = client.get("/metrics", params={"regulation_id": "reg-other"}).json()
    assert empty == []


def test_evaluate_compliance_with_metric(client):
    client.post("/metrics", json=_metric_payload())
    response = client.post(
        "/evaluate",
        json={
            "entity_id": "ent-9",
            "regulation_id": "reg-1",
            "evaluation_data": {"emission_level": 10.0},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["is_compliant"] is True
    assert body["metric_results"]


def test_evaluate_compliance_missing_field(client):
    client.post("/metrics", json=_metric_payload())
    response = client.post(
        "/evaluate",
        json={
            "entity_id": "ent-9",
            "regulation_id": "reg-1",
            "evaluation_data": {"unrelated": 1.0},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_compliant"] is False
    assert any("Missing primary field" in str(r.get("notes", "")) for r in body["metric_results"])


def test_evaluate_compliance_at_location(client):
    client.post("/metrics", json=_metric_payload())
    response = client.post(
        "/evaluate/location",
        json={
            "point": {"lat": 47.6, "lon": -122.33},
            "regulation_ids": ["reg-1"],
            "entity_id": "ent-loc",
            "evaluation_data": {"emission_level": 5.0},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["location"] == {"lat": 47.6, "lon": -122.33}
    assert body["evaluations"][0]["is_compliant"] is True


def test_evaluate_at_location_requires_regulation_ids(client):
    response = client.post(
        "/evaluate/location",
        json={
            "point": {"lat": 47.6, "lon": -122.33},
            "entity_id": "ent-loc",
            "evaluation_data": {"emission_level": 5.0},
        },
    )
    assert response.status_code == 422


def test_summary_report(client):
    client.post("/status", json=_status_payload())
    response = client.post("/reports/summary", json={"title": "Quarterly summary"})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Quarterly summary"
    assert body["regulation_count"] >= 1


def test_entity_report(client):
    client.post("/status", json=_status_payload())
    response = client.post(
        "/reports/entity/ent-1", json={"title": "Entity report"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["entity_id"] == "ent-1"
    assert body["regulation_details"]


def test_regulation_report(client):
    client.post("/status", json=_status_payload())
    response = client.post(
        "/reports/regulation/reg-1", json={"description": "Reg report"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["regulation_id"] == "reg-1"
    assert body["entity_details"]


def test_export_report_summary_json(client):
    client.post("/status", json=_status_payload())
    response = client.post(
        "/reports/export",
        json={"report_type": "summary", "params": {"export_format": "json"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["format"] == "json"
    assert body["data"]["regulation_count"] >= 1


def test_export_report_entity_json(client):
    client.post("/status", json=_status_payload())
    response = client.post(
        "/reports/export",
        json={"report_type": "entity", "entity_id": "ent-1", "params": {}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["entity_id"] == "ent-1"


def test_export_report_html(client):
    response = client.post(
        "/reports/export",
        json={"report_type": "summary", "params": {"export_format": "html"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["format"] == "html"
    assert body["file_path"].endswith(".html")


def test_export_report_invalid_type(client):
    response = client.post(
        "/reports/export",
        json={"report_type": "bogus", "params": {}},
    )
    assert response.status_code == 500
    assert "Error exporting report" in response.json()["detail"]


def test_geo_export(client):
    client.post("/status", json=_status_payload())
    response = client.post("/geo/export", json={"entity_ids": ["ent-1"]})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["feature_count"] >= 1
    assert body["geojson"]["type"] == "FeatureCollection"


def test_geo_export_no_data(client):
    response = client.post("/geo/export", json={"entity_ids": ["ghost-entity"]})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "warning"
    assert body["geojson"] is None
