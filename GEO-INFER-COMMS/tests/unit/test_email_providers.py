"""Failure-contract tests for external email providers."""

import asyncio

import pytest
import requests
from geo_infer_comms.integrations.email_providers import (
    EmailDeliveryError,
    EmailErrorCategory,
    MailgunProvider,
    SendGridProvider,
)


def test_invalid_recipient_raises_typed_validation_error() -> None:
    provider = SendGridProvider({"api_key": "configured"})

    with pytest.raises(EmailDeliveryError) as captured:
        asyncio.run(provider.send_email("not-an-address", "subject", "body"))

    assert captured.value.category is EmailErrorCategory.INVALID_RECIPIENT
    assert captured.value.provider == "sendgrid"
    assert provider.emails_failed == 1


def test_missing_credentials_raise_typed_configuration_error() -> None:
    provider = MailgunProvider({"domain": "example.test"})

    with pytest.raises(EmailDeliveryError) as captured:
        asyncio.run(provider.send_email("person@example.test", "subject", "body"))

    assert captured.value.category is EmailErrorCategory.CONFIGURATION
    assert "api_key" in captured.value.safe_detail


def test_transport_failure_preserves_category_without_secret_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_request(*args: object, **kwargs: object) -> None:
        raise requests.Timeout("provider response contained secret-token")

    monkeypatch.setattr(requests, "post", fail_request)
    provider = SendGridProvider({"api_key": "configured"})

    with pytest.raises(EmailDeliveryError) as captured:
        asyncio.run(provider.send_email("person@example.test", "subject", "body"))

    assert captured.value.category is EmailErrorCategory.TRANSPORT
    assert captured.value.cause_type == "Timeout"
    assert "secret-token" not in str(captured.value)
    assert provider.emails_failed == 1
