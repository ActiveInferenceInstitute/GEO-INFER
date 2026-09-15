"""Regression tests for GIT REST API error handling (500-detail-leak class).

Handlers must map domain failures to 4xx with the domain message; any
non-domain exception must escape to ``ErrorHandlerMiddleware`` and produce a
generic HTTP 500 whose body never contains the internal exception text
(mirrors GEO-INFER-LOG ``tests/unit/test_api_error_handling.py``, LOG-EXC-01).
"""

import pytest
from fastapi.testclient import TestClient

import geo_infer_git.api.rest_api as rest_api
from geo_infer_git.api.rest_api import get_repo_manager


class _StubManager:
    """Repo manager stub whose branch methods raise or return as configured."""

    def __init__(self, branches=None, exc=None):
        self._branches = branches if branches is not None else []
        self._exc = exc

    def list_branches(self, repo_id):
        if self._exc is not None:
            raise self._exc
        return self._branches

    def create_branch_for_repository(self, repo_id, name, base, protected=False):
        if self._exc is not None:
            raise self._exc
        return {
            "name": name,
            "commit_sha": "0" * 40,
            "commit_message": "stub",
            "author": "tester",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "protected": protected,
            "ahead": 0,
            "behind": 0,
        }


@pytest.fixture
def client():
    """TestClient on the module-level app with a clean override table."""
    rest_api.app.dependency_overrides.clear()
    test_client = TestClient(rest_api.app)
    yield test_client
    rest_api.app.dependency_overrides.clear()


def test_create_branch_value_error_maps_to_400_with_domain_message(client):
    """A domain ValueError from branch creation surfaces as 400, not 500."""
    rest_api.app.dependency_overrides[get_repo_manager] = lambda: _StubManager(
        exc=ValueError("branch name already exists")
    )

    response = client.post(
        "/repositories/repo-1/branches", json={"name": "feature", "base": "main"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "branch name already exists"


def test_create_branch_unexpected_error_returns_generic_500(client):
    """A non-domain TypeError must become a generic 500 without the message."""
    leak = "'NoneType' object is not subscriptable"
    rest_api.app.dependency_overrides[get_repo_manager] = lambda: _StubManager(
        exc=TypeError(leak)
    )

    response = client.post(
        "/repositories/repo-1/branches", json={"name": "feature", "base": "main"}
    )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert leak not in response.text


def test_list_branches_unknown_status_filter_returns_400(client):
    """A bad status_filter is a client fault: 400, never rewrapped as 500."""
    rest_api.app.dependency_overrides[get_repo_manager] = lambda: _StubManager(
        branches=[{"name": "main", "protected": False}]
    )

    response = client.get(
        "/repositories/repo-1/branches", params={"status_filter": "bogus"}
    )

    assert response.status_code == 400
    assert "bogus" in response.json()["detail"]


def test_list_branches_unexpected_error_returns_generic_500(client):
    """A non-domain RuntimeError while listing branches stays generic."""
    leak = "connection reset by peer"
    rest_api.app.dependency_overrides[get_repo_manager] = lambda: _StubManager(
        exc=RuntimeError(leak)
    )

    response = client.get("/repositories/repo-1/branches")

    assert response.status_code == 500
    assert leak not in response.text


def test_list_branches_missing_repo_returns_404(client):
    """Missing repository keeps its domain 404 mapping."""
    rest_api.app.dependency_overrides[get_repo_manager] = lambda: _StubManager(
        exc=FileNotFoundError("repository repo-1 not found")
    )

    response = client.get("/repositories/repo-1/branches")

    assert response.status_code == 404


def test_get_system_status_unexpected_error_returns_generic_500(client, monkeypatch):
    """A failing status check must not leak the underlying exception text."""
    leak = "archive member is corrupt"

    class _BrokenStatus:
        def check_repo_status(self):
            raise ValueError(leak)

    monkeypatch.setattr(rest_api, "repo_manager", _BrokenStatus())

    response = client.get("/system/status")

    assert response.status_code == 500
    assert response.json()["error"]["message"] == "An unexpected error occurred"
    assert leak not in response.text


def test_get_repository_unknown_returns_404(client, monkeypatch):
    """Unchanged behavior: unknown repository ids still return 404."""
    monkeypatch.setattr(rest_api, "repository_records", {})
    rest_api.app.dependency_overrides[get_repo_manager] = lambda: _StubManager()

    response = client.get("/repositories/nope")

    assert response.status_code == 404
