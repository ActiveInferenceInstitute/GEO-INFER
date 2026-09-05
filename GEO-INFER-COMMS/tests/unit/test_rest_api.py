"""Regression tests for REST API error and configuration contracts."""

import asyncio
import inspect
import os
import time
from types import SimpleNamespace

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



class TestCredentialValidation:
    def _credentials(self, token: str):
        return SimpleNamespace(credentials=token)

    def test_valid_jwt_returns_subject(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import jwt as pyjwt

        monkeypatch.setenv("COMMS_JWT_SECRET", "unit-test-secret-0123456789abcdef-0123456789abcdef")
        api = _api()
        token = pyjwt.encode(
            {"sub": "alice", "exp": int(time.time()) + 60},
            "unit-test-secret-0123456789abcdef-0123456789abcdef",
            algorithm="HS256",
        )

        user_id = api._validate_credentials(self._credentials(token))

        assert user_id == "alice"

    def test_invalid_jwt_is_rejected_with_401(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import jwt as pyjwt

        monkeypatch.setenv("COMMS_JWT_SECRET", "correct-secret-0123456789abcdef-0123456789abcdef")
        api = _api()
        # Signed with the wrong secret → decode fails → must be rejected
        bad_token = pyjwt.encode(
            {"sub": "attacker", "exp": int(time.time()) + 60},
            "wrong-secret-0123456789abcdef-0123456789abcdef",
            algorithm="HS256",
        )

        with pytest.raises(HTTPException) as error:
            api._validate_credentials(self._credentials(bad_token))

        assert error.value.status_code == 401

    def test_expired_jwt_is_rejected_with_401(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import jwt as pyjwt

        monkeypatch.setenv("COMMS_JWT_SECRET", "correct-secret-0123456789abcdef-0123456789abcdef")
        api = _api()
        expired = pyjwt.encode(
            {"sub": "alice", "exp": int(time.time()) - 60},
            "correct-secret-0123456789abcdef-0123456789abcdef",
            algorithm="HS256",
        )

        with pytest.raises(HTTPException) as error:
            api._validate_credentials(self._credentials(expired))

        assert error.value.status_code == 401

    def test_hash_fallback_applies_without_jwt_secret(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import hashlib

        monkeypatch.delenv("COMMS_JWT_SECRET", raising=False)
        api = _api()

        user_id = api._validate_credentials(self._credentials("raw-opaque-token"))

        expected = "user_" + hashlib.sha256(b"raw-opaque-token").hexdigest()[:8]
        assert user_id == expected