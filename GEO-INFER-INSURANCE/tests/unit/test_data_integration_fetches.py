"""Failure-semantics tests for underwriting data integration fetches (PL-03).

Contract: unconfigured placeholder sources (built-in defaults with entirely
unset credentials) raise ValueError naming the source and never attempt
network egress; for configured sources, expected transport/config failures
(OSError/KeyError/ValueError) log a warning and return None so an outage is
visible in logs; unexpected errors propagate instead of masquerading as
"no record".
"""

import logging

import pytest

from geo_infer_insurance.underwriting.utils.data_integration import (
    DataIntegrationManager,
    get_credit_score,
    get_property_history,
)

MODULE_LOGGER = "geo_infer_insurance.underwriting.utils.data_integration"


class ExplodingDataManager(DataIntegrationManager):
    """Manager double whose get_data raises the configured exception."""

    def __init__(self, exc: BaseException):
        self.exc = exc

    def get_data(self, source_name, query_parameters=None):
        raise self.exc


class NoRecordDataManager(DataIntegrationManager):
    """Manager double representing a successful lookup with no record."""

    def __init__(self):
        pass

    def get_data(self, source_name, query_parameters=None):
        return None


def test_credit_bureau_connection_error_logs_warning_and_returns_none(caplog):
    manager = ExplodingDataManager(ConnectionError("credit-bureau unreachable"))
    with caplog.at_level(logging.WARNING, logger=MODULE_LOGGER):
        assert get_credit_score("123-45-6789", data_manager=manager) is None
    assert any(
        "Credit bureau fetch failed" in record.getMessage() for record in caplog.records
    )


def test_property_database_timeout_logs_warning_and_returns_none(caplog):
    manager = ExplodingDataManager(TimeoutError("property-db timed out"))
    with caplog.at_level(logging.WARNING, logger=MODULE_LOGGER):
        assert get_property_history("prop-1", data_manager=manager) is None
    assert any(
        "Property database fetch failed" in record.getMessage()
        for record in caplog.records
    )


def test_unexpected_error_propagates_from_credit_score():
    manager = ExplodingDataManager(RuntimeError("wiring bug"))
    with pytest.raises(RuntimeError):
        get_credit_score("123-45-6789", data_manager=manager)


def test_unexpected_error_propagates_from_property_history():
    manager = ExplodingDataManager(RuntimeError("wiring bug"))
    with pytest.raises(RuntimeError):
        get_property_history("prop-1", data_manager=manager)


def test_no_record_returns_none_without_fetch_warning(caplog):
    """A successful no-record lookup is not logged as an outage."""
    with caplog.at_level(logging.WARNING, logger=MODULE_LOGGER):
        assert (
            get_credit_score("123-45-6789", data_manager=NoRecordDataManager()) is None
        )
    assert not any(
        "Credit bureau fetch failed" in record.getMessage() for record in caplog.records
    )


PLACEHOLDER_SOURCE_NAMES = (
    "credit_bureau",
    "property_database",
    "weather_data",
    "claims_history",
)
_PLACEHOLDER_ENV_KEYS = (
    "CREDIT_BUREAU_API_KEY",
    "PROPERTY_DB_API_KEY",
    "WEATHER_API_KEY",
    "CLAIMS_DB_USER",
    "CLAIMS_DB_PASSWORD",
)


def _forbid_requests_get(monkeypatch):
    """Make any requests.get call explode; a no-op when requests is absent."""
    try:
        import requests
    except ImportError:
        return

    def _explode(*args, **kwargs):
        raise AssertionError("network egress attempted for unconfigured source")

    monkeypatch.setattr(requests, "get", _explode)


def test_placeholder_source_get_data_raises_loudly(monkeypatch):
    """get_data('credit_bureau', ...) never returns bare None: it raises."""
    for var in _PLACEHOLDER_ENV_KEYS:
        monkeypatch.delenv(var, raising=False)
    _forbid_requests_get(monkeypatch)
    manager = DataIntegrationManager()
    with pytest.raises(ValueError, match="credit_bureau"):
        manager.get_data("credit_bureau", {"ssn": "123-45-6789"})


def test_all_placeholder_defaults_raise_without_egress(monkeypatch):
    for var in _PLACEHOLDER_ENV_KEYS:
        monkeypatch.delenv(var, raising=False)
    _forbid_requests_get(monkeypatch)
    manager = DataIntegrationManager()
    for name in PLACEHOLDER_SOURCE_NAMES:
        with pytest.raises(ValueError, match=name):
            manager.get_data(name, {"test": True})


def test_configured_source_is_fetched_and_cached(monkeypatch):
    """A source with configured credentials skips the placeholder refusal."""
    monkeypatch.setenv("CREDIT_BUREAU_API_KEY", "test-key")
    manager = DataIntegrationManager(data_sources=["credit_bureau"])
    calls = []

    def fake_fetch(source, query_parameters=None):
        calls.append(source.name)
        return {"credit_score": 700}

    monkeypatch.setattr(manager, "_fetch_data_from_source", fake_fetch)
    assert manager.get_data("credit_bureau", {"ssn": "x"}) == {"credit_score": 700}
    assert calls == ["credit_bureau"]
