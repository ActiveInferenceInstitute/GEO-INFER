"""Tests for the audit logging module."""
import pytest
import json
from datetime import datetime
from pathlib import Path

from geo_infer_sec.core.audit import (
    AuditEvent,
    AuditEventType,
    AuditEventSeverity,
    AuditLogger,
)


class TestAuditEvent:
    def test_create_event(self):
        event = AuditEvent(
            event_id="evt-001",
            event_type=AuditEventType.AUTHENTICATION,
            timestamp=datetime.now(),
            user_id="user-1",
            action="login",
            result="success",
        )
        assert event.event_id == "evt-001"
        assert event.event_type == AuditEventType.AUTHENTICATION

    def test_to_dict(self):
        event = AuditEvent(
            event_id="evt-002",
            event_type=AuditEventType.DATA_ACCESS,
            timestamp=datetime.now(),
            user_id="user-2",
            resource="dataset-x",
            action="read",
        )
        d = event.to_dict()
        assert d["event_id"] == "evt-002"
        assert d["event_type"] == "data_access"
        assert isinstance(d["timestamp"], str)

    def test_to_json(self):
        event = AuditEvent(
            event_id="evt-003",
            event_type=AuditEventType.SECURITY_EVENT,
            timestamp=datetime.now(),
            severity=AuditEventSeverity.HIGH,
        )
        j = event.to_json()
        parsed = json.loads(j)
        assert parsed["severity"] == "high"

    def test_event_with_details(self):
        event = AuditEvent(
            event_id="evt-004",
            event_type=AuditEventType.AUTHORIZATION,
            timestamp=datetime.now(),
            details={"permission": "read", "resource_type": "geospatial"},
        )
        assert event.details["permission"] == "read"


class TestAuditLogger:
    def test_init(self, tmp_path):
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=log_file)
        assert logger.retention_days == 90

    def test_log_event(self, tmp_path):
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=log_file)
        logger.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            user_id="user-1",
            action="login",
            result="success",
        )
        assert len(logger.events) == 1

    def test_log_multiple_events(self, tmp_path):
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=log_file)
        for i in range(5):
            logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=f"user-{i}",
                action="read",
            )
        assert len(logger.events) == 5

    def test_log_event_severity(self, tmp_path):
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=log_file)
        logger.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            severity=AuditEventSeverity.CRITICAL,
            action="intrusion_detected",
        )
        assert logger.events[0].severity == AuditEventSeverity.CRITICAL

    def test_query_events_by_type(self, tmp_path):
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=log_file)
        logger.log_event(event_type=AuditEventType.AUTHENTICATION, action="login")
        logger.log_event(event_type=AuditEventType.DATA_ACCESS, action="read")
        logger.log_event(event_type=AuditEventType.AUTHENTICATION, action="logout")
        auth_events = [e for e in logger.events if e.event_type == AuditEventType.AUTHENTICATION]
        assert len(auth_events) == 2
