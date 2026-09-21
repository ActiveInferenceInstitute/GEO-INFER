"""Tests for the store-backed performance-review API endpoints (M7-02).

POST/GET /pep/performance/reviews must persist through
``performance_review_store`` and validate payloads (400 on missing
employee_id or a ``PerformanceReview``-invalid body).
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_pep.api import api_router
from geo_infer_pep.api.errors import register_error_handlers
from geo_infer_pep.core.data_store import pep_data_manager as store
from geo_infer_pep.performance_store import performance_review_store


@pytest.fixture
def client():
    """TestClient mounting the full api_router with shared error handling."""
    store.clear_all_data()
    performance_review_store.clear()
    app = FastAPI()
    app.include_router(api_router)
    register_error_handlers(app)
    test_client = TestClient(app)
    yield test_client
    store.clear_all_data()
    performance_review_store.clear()


def test_create_and_get_performance_review_round_trip(client):
    """A created review persists in the store and is returned by GET."""
    create_response = client.post(
        "/pep/performance/reviews",
        json={
            "employee_id": "emp-1",
            "review_id": "rev-1",
            "review_date": "2026-08-01",
            "reviewer_id": "mgr-9",
            "overall_rating": 4.5,
            "comments": "solid",
        },
    )

    assert create_response.status_code == 200
    body = create_response.json()
    assert body["message"] == "Performance review created"
    assert body["data"]["review_date"] == "2026-08-01"

    get_response = client.get("/pep/performance/reviews/emp-1")

    assert get_response.status_code == 200
    get_body = get_response.json()
    assert len(get_body["reviews"]) == 1
    assert get_body["reviews"][0]["review_id"] == "rev-1"
    assert get_body["reviews"][0]["overall_rating"] == 4.5
    assert len(performance_review_store.reviews_by_employee["emp-1"]) == 1


def test_create_review_for_second_employee_does_not_cross_leak(client):
    """Reviews for different employees stay isolated in the store."""
    for employee_id, review_id in (("emp-1", "rev-1"), ("emp-2", "rev-2")):
        response = client.post(
            "/pep/performance/reviews",
            json={
                "employee_id": employee_id,
                "review_id": review_id,
                "review_date": "2026-08-01",
                "reviewer_id": "mgr-9",
                "overall_rating": 4.0,
            },
        )
        assert response.status_code == 200

    first = client.get("/pep/performance/reviews/emp-1").json()
    second = client.get("/pep/performance/reviews/emp-2").json()

    assert [r["review_id"] for r in first["reviews"]] == ["rev-1"]
    assert [r["review_id"] for r in second["reviews"]] == ["rev-2"]


def test_get_performance_reviews_unknown_employee_returns_empty(client):
    """GET for an employee with no reviews returns an empty list."""
    response = client.get("/pep/performance/reviews/nobody")

    assert response.status_code == 200
    assert response.json() == {"employee_id": "nobody", "reviews": []}


def test_create_performance_review_requires_employee_id(client):
    """POST without employee_id is a 400 naming employee_id."""
    response = client.post(
        "/pep/performance/reviews",
        json={
            "review_id": "rev-1",
            "review_date": "2026-08-01",
            "reviewer_id": "mgr-9",
            "overall_rating": 4.5,
        },
    )

    assert response.status_code == 400
    assert "employee_id" in response.json()["detail"]


def test_create_performance_review_rejects_invalid_payload(client):
    """POST missing required PerformanceReview fields is a 400."""
    response = client.post("/pep/performance/reviews", json={"employee_id": "emp-1"})

    assert response.status_code == 400
