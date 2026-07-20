"""Regression tests for REST API error and configuration contracts."""

import asyncio
import inspect

import pytest
from fastapi import BackgroundTasks, HTTPException

from geo_infer_comms import GeospatialCommunicationSystem, MessageRequest
from geo_infer_comms.api.rest_api import CommunicationAPI


def _api() -> CommunicationAPI:
    system = GeospatialCommunicationSystem(config={"enable_persistence": False})
    return CommunicationAPI(system, enable_auth=False, enable_cors=False)


def test_cors_origins_default_is_not_mutable() -> None:
    parameter = inspect.signature(CommunicationAPI).parameters["cors_origins"]
    assert parameter.default is None


def test_invalid_message_content_preserves_http_400() -> None:
    api = _api()
    route = next(route for route in api.app.routes if route.path == "/messages")
    request = MessageRequest(content="   ", recipients=["recipient"])

    with pytest.raises(HTTPException) as error:
        asyncio.run(route.endpoint(request, BackgroundTasks(), None))

    assert error.value.status_code == 400
    assert error.value.detail == "Invalid message content"
