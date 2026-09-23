"""Store-backed round-trip tests for learning, conflict, and survey endpoints (GS19-17).

The four former echo-stub route groups must persist through the shared
``pep_data_manager``: POST stores the record, GET returns stored records.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_pep.api import api_router
from geo_infer_pep.api.errors import register_error_handlers
from geo_infer_pep.core.data_store import pep_data_manager as store


@pytest.fixture
def client():
    """TestClient mounting the full api_router with a cleared shared store."""
    store.clear_all_data()
    app = FastAPI()
    app.include_router(api_router)
    register_error_handlers(app)
    test_client = TestClient(app)
    yield test_client
    store.clear_all_data()


# --- Learning & Development -------------------------------------------------


def test_learning_course_post_then_get_round_trip(client):
    created = client.post(
        "/pep/learning/courses",
        json={
            "course_id": "course-1",
            "title": "Onboarding Basics",
            "category": "compliance",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["message"] == "Learning course created"
    assert body["data"]["course_id"] == "course-1"

    listing = client.get("/pep/learning/courses")
    assert listing.status_code == 200
    assert listing.json()["courses"] == [body["data"]]


def test_create_duplicate_learning_course_returns_409(client):
    payload = {"course_id": "course-1", "title": "Onboarding Basics"}
    assert client.post("/pep/learning/courses", json=payload).status_code == 200
    conflict = client.post("/pep/learning/courses", json=payload)
    assert conflict.status_code == 409
    assert "already exists" in conflict.json()["detail"]


def test_create_learning_course_rejects_invalid_payload(client):
    response = client.post("/pep/learning/courses", json={"title": "No id"})
    assert response.status_code == 400


def test_enrollment_requires_existing_course(client):
    response = client.post(
        "/pep/learning/enrollments",
        json={"enrollment_id": "enr-1", "employee_id": "emp-1", "course_id": "ghost"},
    )
    assert response.status_code == 404


def test_enrollment_persists_and_filters_apply(client):
    client.post(
        "/pep/learning/courses",
        json={"course_id": "course-1", "title": "Security 101"},
    )
    client.post(
        "/pep/learning/courses",
        json={"course_id": "course-2", "title": "Python 101"},
    )
    first = client.post(
        "/pep/learning/enrollments",
        json={
            "enrollment_id": "enr-1",
            "employee_id": "emp-1",
            "course_id": "course-1",
        },
    )
    assert first.status_code == 200
    client.post(
        "/pep/learning/enrollments",
        json={
            "enrollment_id": "enr-2",
            "employee_id": "emp-2",
            "course_id": "course-2",
        },
    )

    all_enrollments = client.get("/pep/learning/enrollments")
    assert [e["enrollment_id"] for e in all_enrollments.json()["enrollments"]] == [
        "enr-1",
        "enr-2",
    ]

    by_employee = client.get(
        "/pep/learning/enrollments", params={"employee_id": "emp-1"}
    )
    assert [e["course_id"] for e in by_employee.json()["enrollments"]] == ["course-1"]


# --- Conflict resolution ------------------------------------------------------


def test_conflict_case_round_trip_and_update(client):
    created = client.post(
        "/pep/conflicts/cases",
        json={
            "case_id": "case-1",
            "title": "Desk dispute",
            "parties": ["emp-1", "emp-2"],
        },
    )
    assert created.status_code == 200
    assert created.json()["data"]["status"] == "open"

    listing = client.get("/pep/conflicts/cases")
    assert [c["case_id"] for c in listing.json()["cases"]] == ["case-1"]

    updated = client.put(
        "/pep/conflicts/cases/case-1",
        json={"status": "resolved", "resolution_notes": "Mediated"},
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["data"]["status"] == "resolved"
    assert body["data"]["resolution_notes"] == "Mediated"
    assert body["data"]["parties"] == ["emp-1", "emp-2"]

    stored = client.get("/pep/conflicts/cases").json()["cases"]
    assert stored == [body["data"]]


def test_update_missing_conflict_case_returns_404(client):
    response = client.put("/pep/conflicts/cases/ghost", json={"status": "resolved"})
    assert response.status_code == 404


def test_update_conflict_case_rejects_id_change(client):
    client.post("/pep/conflicts/cases", json={"case_id": "case-1", "title": "T"})
    response = client.put("/pep/conflicts/cases/case-1", json={"case_id": "case-2"})
    assert response.status_code == 400


# --- Surveys ------------------------------------------------------------------


def test_survey_and_response_round_trip(client):
    created = client.post(
        "/pep/surveys",
        json={
            "survey_id": "survey-1",
            "title": "Engagement Q4",
            "questions": ["q1", "q2"],
        },
    )
    assert created.status_code == 200

    submitted = client.post(
        "/pep/surveys/survey-1/responses",
        json={"response_id": "resp-1", "answers": {"q1": "good"}},
    )
    assert submitted.status_code == 200
    assert submitted.json()["data"]["survey_id"] == "survey-1"

    responses = client.get("/pep/surveys/survey-1/responses")
    assert responses.status_code == 200
    assert responses.json() == {
        "survey_id": "survey-1",
        "responses": [submitted.json()["data"]],
    }


def test_survey_responses_unknown_survey_returns_404(client):
    response = client.get("/pep/surveys/nope/responses")
    assert response.status_code == 404


def test_survey_response_unknown_survey_returns_404(client):
    response = client.post(
        "/pep/surveys/nope/responses", json={"response_id": "resp-x", "answers": {}}
    )
    assert response.status_code == 404
