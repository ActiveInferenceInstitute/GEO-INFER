"""Regression tests for transport API error handling (GS-223).

Domain ``ValueError``s raised by core logic are client faults and must map to
HTTP 400. Unexpected exceptions (TypeError, AttributeError, ...) are server
faults and must surface as HTTP 500 with a generic message instead of being
masked as 400s that leak internal exception text.
"""

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_log.api.errors import register_error_handlers
from geo_infer_log.api.transport import get_multimodal_planner, router


class _FailingPlanner:
    """Stub planner whose plan_route raises the configured exception."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def plan_route(self, **kwargs: Any) -> Dict[str, Any]:
        raise self._exc


def _client(planner: Any) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    register_error_handlers(app)
    app.dependency_overrides[get_multimodal_planner] = lambda: planner
    return TestClient(app)


def _route_payload() -> Dict[str, Any]:
    return {
        "origin": [13.404954, 52.520008],
        "destination": [13.36, 52.49],
        "allowed_modes": ["car"],
        "preferences": None,
    }


class TestTransportErrorMapping:
    """plan_route must distinguish domain errors from server faults."""

    def test_domain_value_error_maps_to_400(self) -> None:
        """A domain ValueError from the planner becomes a 400 with its message."""
        client = _client(_FailingPlanner(ValueError("Route could not be completed")))

        response = client.post("/transport/route", json=_route_payload())

        assert response.status_code == 400
        assert "Route could not be completed" in response.json()["detail"]

    def test_type_error_surfaces_as_500(self) -> None:
        """A TypeError is a server fault: 500 with a generic, non-leaking body."""
        client = _client(
            _FailingPlanner(TypeError("'int' object is not subscriptable"))
        )

        response = client.post("/transport/route", json=_route_payload())

        assert response.status_code == 500
        body = response.json()
        assert body["error"]["code"] == "INTERNAL_ERROR"
        assert "not subscriptable" not in response.text

    def test_attribute_error_surfaces_as_500(self) -> None:
        """AttributeError (e.g. from a malformed internal object) is a 500 too."""
        client = _client(_FailingPlanner(AttributeError("'NoneType' has no 'graph'")))

        response = client.post("/transport/route", json=_route_payload())

        assert response.status_code == 500
        assert response.json()["error"]["status_code"] == 500
