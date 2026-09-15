"""Regression tests for PEP API error handling (500-detail-leak class).

Domain failures (``ValueError``/``FileNotFoundError`` from the CSV import
path) map to 400 with the domain message; any non-domain exception must
escape to the shared ``ErrorHandlerMiddleware`` and produce a generic HTTP
500 whose body never contains the internal exception text (mirrors
GEO-INFER-LOG ``tests/unit/test_api_error_handling.py``, LOG-EXC-01).
"""

import io

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import geo_infer_pep.api.crm_endpoints as crm_endpoints
import geo_infer_pep.api.hr_endpoints as hr_endpoints
import geo_infer_pep.api.talent_endpoints as talent_endpoints
import geo_infer_pep.utils.uploads as uploads
from geo_infer_pep.api.errors import register_error_handlers
from geo_infer_pep.core.data_store import pep_data_manager as store


@pytest.fixture
def client():
    """TestClient hosting the PEP routers with shared error handling."""
    store.clear_all_data()
    app = FastAPI()
    app.include_router(crm_endpoints.router)
    app.include_router(hr_endpoints.router)
    app.include_router(talent_endpoints.router)
    register_error_handlers(app)
    test_client = TestClient(app)
    yield test_client
    store.clear_all_data()


def _upload(client, path, content, filename="data.csv"):
    """POST a CSV payload as a multipart upload."""
    return client.post(
        path, files={"file": (filename, io.BytesIO(content.encode()), "text/csv")}
    )


class _StubTalentImporter:
    """Replaces CSVTalentImporter with an import_candidates that raises."""

    def __init__(self, exc):
        self._exc = exc

    def import_candidates(self):
        raise self._exc


def test_talent_upload_success_path_unchanged(client):
    """A valid candidate CSV still imports and returns the success message."""
    response = _upload(
        client,
        "/talent/upload/candidates/csv",
        "candidate_id,first_name,last_name,email\nt-1,Ada,Lovelace,ada@example.com\n",
    )

    assert response.status_code == 200
    assert "Imported 1 candidates" in response.json()["message"]
    assert len(store.candidates) == 1


def test_talent_upload_domain_value_error_maps_to_400(client, monkeypatch):
    """A domain ValueError from the import path surfaces as 400, not 500."""
    monkeypatch.setattr(
        talent_endpoints,
        "CSVTalentImporter",
        lambda **_: _StubTalentImporter(
            ValueError("At least one CSV path is required")
        ),
    )

    response = _upload(
        client,
        "/talent/upload/candidates/csv",
        "candidate_id,first_name,last_name,email\nt-1,A,B,a@example.com\n",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "At least one CSV path is required"


def test_talent_upload_unexpected_error_returns_generic_500(client, monkeypatch):
    """A non-domain TypeError must become a generic 500 without the message."""
    leak = "'int' object is not iterable"
    monkeypatch.setattr(
        talent_endpoints,
        "CSVTalentImporter",
        lambda **_: _StubTalentImporter(TypeError(leak)),
    )

    response = _upload(
        client,
        "/talent/upload/candidates/csv",
        "candidate_id,first_name,last_name,email\nt-1,A,B,a@example.com\n",
    )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert leak not in response.text


def test_crm_upload_success_path_unchanged(client):
    """A valid customer CSV still imports and reports the imported count."""
    response = _upload(
        client,
        "/crm/upload/csv?clean_data=false&enrich_data=false",
        "id,last_name\nc-1,Doe\n",
    )

    assert response.status_code == 200
    assert response.json()["imported_count"] == 1


def test_crm_upload_unexpected_error_returns_generic_500(client, monkeypatch):
    """A non-domain failure during CRM CSV processing stays generic."""
    leak = "invalid literal for int()"

    class _ExplodingImporter:
        def __init__(self, file_path):
            pass

        def import_customers(self):
            raise TypeError(leak)

    monkeypatch.setattr(crm_endpoints, "CSVCRMImporter", _ExplodingImporter)

    response = _upload(
        client, "/crm/upload/csv?clean_data=false&enrich_data=false", "id,last_name\n"
    )

    assert response.status_code == 500
    assert leak not in response.text


def test_hr_upload_unexpected_error_returns_generic_500(client, monkeypatch):
    """A non-domain failure during HR CSV processing stays generic."""
    leak = "list index out of range"

    class _ExplodingImporter:
        def __init__(self, file_path):
            pass

        def import_employees(self):
            raise TypeError(leak)

    monkeypatch.setattr(hr_endpoints, "CSVHRImporter", _ExplodingImporter)

    response = _upload(
        client, "/hr/upload/csv?clean_data=false&enrich_data=false", "employee_id\n"
    )

    assert response.status_code == 500
    assert leak not in response.text


def test_upload_save_failure_returns_generic_500(client, monkeypatch):
    """save_upload_file_tmp maps write failures to a generic 500 (no leak)."""
    leak = "disk full"

    def _boom(*args, **kwargs):
        raise OSError(leak)

    monkeypatch.setattr(uploads.tempfile, "NamedTemporaryFile", _boom)

    response = _upload(
        client,
        "/talent/upload/candidates/csv",
        "candidate_id,first_name,last_name,email\nt-1,A,B,a@example.com\n",
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Could not save uploaded file"
    assert leak not in response.text
