"""Failure-semantics tests for underwriting data integration fetches (PL-03).

Contract: expected transport/config failures (OSError/KeyError/ValueError)
log a warning and return None so an outage is visible in logs; unexpected
errors propagate instead of masquerading as "no record".
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
        "Credit bureau fetch failed" in record.getMessage()
        for record in caplog.records
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
        assert get_credit_score("123-45-6789", data_manager=NoRecordDataManager()) is None
    assert not any(
        "Credit bureau fetch failed" in record.getMessage()
        for record in caplog.records
    )
