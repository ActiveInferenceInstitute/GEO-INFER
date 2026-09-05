"""Tests for the compliance tracking module."""
import datetime
import uuid
import pytest

from geo_infer_norms.core.compliance_tracking import ComplianceTracker, ComplianceReport
from geo_infer_norms.models.compliance_status import ComplianceStatus, ComplianceMetric
from geo_infer_norms.models.regulation import Regulation
from geo_infer_norms.models.legal_entity import LegalEntity


def _make_status(entity_id: str, regulation_id: str, is_compliant: bool, level: float = 1.0, days_ago: int = 0) -> ComplianceStatus:
    ts = datetime.datetime.now() - datetime.timedelta(days=days_ago)
    return ComplianceStatus(
        id=str(uuid.uuid4()),
        entity_id=entity_id,
        regulation_id=regulation_id,
        is_compliant=is_compliant,
        compliance_level=level,
        timestamp=ts,
        notes="test",
    )


def _make_regulation(reg_id: str = "reg-1") -> Regulation:
    return Regulation(
        id=reg_id,
        name="Test Regulation",
        description="A test regulation",
        regulation_type="environmental",
        issuing_authority="EPA",
        effective_date=datetime.date(2020, 1, 1),
    )


def _make_entity(ent_id: str = "ent-1") -> LegalEntity:
    return LegalEntity(
        id=ent_id,
        name="Test Entity",
        entity_type="facility",
    )


def _make_metric(reg_id: str = "reg-1", eval_type: str = "threshold") -> ComplianceMetric:
    return ComplianceMetric.create(
        name="Test Metric",
        description="A test metric",
        regulation_id=reg_id,
        evaluation_type=eval_type,
        primary_field="emission_level",
        required_fields=["emission_level"],
        threshold_value=50.0,
        comparison="less_than",
    )


class TestComplianceTracker:
    def test_init(self):
        tracker = ComplianceTracker(name="test-tracker", description="Test")
        assert tracker.name == "test-tracker"
        assert len(tracker.compliance_statuses) == 0

    def test_add_compliance_status(self):
        tracker = ComplianceTracker(name="test")
        status = _make_status("ent-1", "reg-1", True)
        tracker.add_compliance_status(status)
        assert len(tracker.compliance_statuses) == 1

    def test_get_entity_compliance_found(self):
        tracker = ComplianceTracker(name="test")
        tracker.add_compliance_status(_make_status("ent-1", "reg-1", True))
        tracker.add_compliance_status(_make_status("ent-1", "reg-2", False, 0.3))
        result = tracker.get_entity_compliance("ent-1")
        assert result["entity_id"] == "ent-1"
        assert result["compliance_count"] == 1
        assert result["non_compliance_count"] == 1

    def test_get_entity_compliance_not_found(self):
        tracker = ComplianceTracker(name="test")
        result = tracker.get_entity_compliance("nonexistent")
        assert result["status"] == "unknown"

    def test_get_regulation_compliance(self):
        tracker = ComplianceTracker(name="test")
        tracker.add_compliance_status(_make_status("ent-1", "reg-1", True))
        tracker.add_compliance_status(_make_status("ent-2", "reg-1", False, 0.2))
        result = tracker.get_regulation_compliance("reg-1")
        assert result["entity_count"] == 2
        assert result["compliant_count"] == 1

    def test_evaluate_compliance_threshold(self):
        reg = _make_regulation("reg-1")
        entity = _make_entity("ent-1")
        metric = _make_metric("reg-1", "threshold")
        tracker = ComplianceTracker(name="test", compliance_metrics=[metric])
        status = tracker.evaluate_compliance(entity, reg, {"emission_level": 30.0})
        assert status.is_compliant is True
        assert status.compliance_level == 1.0

    def test_evaluate_compliance_fails_threshold(self):
        reg = _make_regulation("reg-1")
        entity = _make_entity("ent-1")
        metric = _make_metric("reg-1", "threshold")
        tracker = ComplianceTracker(name="test", compliance_metrics=[metric])
        status = tracker.evaluate_compliance(entity, reg, {"emission_level": 80.0})
        assert status.is_compliant is False

    def test_evaluate_compliance_range(self):
        reg = _make_regulation("reg-1")
        entity = _make_entity("ent-1")
        metric = ComplianceMetric.create(
            name="pH Level",
            description="pH must be 6.5-8.5",
            regulation_id="reg-1",
            evaluation_type="range",
            primary_field="ph_level",
            range_min=6.5,
            range_max=8.5,
        )
        tracker = ComplianceTracker(name="test", compliance_metrics=[metric])
        status = tracker.evaluate_compliance(entity, reg, {"ph_level": 7.0})
        assert status.is_compliant is True

    def test_evaluate_compliance_boolean(self):
        reg = _make_regulation("reg-1")
        entity = _make_entity("ent-1")
        metric = ComplianceMetric.create(
            name="Has Permit",
            description="Must have permit",
            regulation_id="reg-1",
            evaluation_type="boolean",
            primary_field="has_permit",
        )
        tracker = ComplianceTracker(name="test", compliance_metrics=[metric])
        status = tracker.evaluate_compliance(entity, reg, {"has_permit": True})
        assert status.is_compliant is True

    def test_evaluate_compliance_missing_primary_field_is_non_compliant_with_note(self):
        """A missing primary_field must not silently evaluate as 0/False."""
        reg = _make_regulation("reg-1")
        entity = _make_entity("ent-1")
        metric = ComplianceMetric.create(
            name="test_metric",
            description="Threshold metric with explicit required_fields",
            regulation_id="reg-1",
            evaluation_type="threshold",
            primary_field="pm25",
            threshold_value=35,
            comparison="less_than",
            required_fields=["station_id"],
        )
        tracker = ComplianceTracker(name="test", compliance_metrics=[metric])
        status = tracker.evaluate_compliance(entity, reg, {"station_id": "s-1"})
        assert status.is_compliant is False
        assert status.compliance_level == 0.0
        assert status.metric_results is not None
        assert "pm25" in status.metric_results[0]["notes"]


class TestComplianceReport:
    def test_generate_summary_report(self):
        tracker = ComplianceTracker(name="test")
        tracker.add_compliance_status(_make_status("ent-1", "reg-1", True))
        tracker.add_compliance_status(_make_status("ent-2", "reg-1", False, 0.3))
        report = ComplianceReport(tracker, title="Test Report")
        summary = report.generate_summary_report()
        assert summary["title"] == "Test Report"
        assert summary["entity_count"] == 2
        assert summary["compliant_count"] == 1

    def test_generate_entity_report(self):
        tracker = ComplianceTracker(name="test")
        tracker.add_compliance_status(_make_status("ent-1", "reg-1", True))
        report = ComplianceReport(tracker)
        entity_report = report.generate_entity_report("ent-1")
        assert entity_report["entity_id"] == "ent-1"
        assert entity_report["overall_status"] == "compliant"

    def test_generate_regulation_report(self):
        tracker = ComplianceTracker(name="test")
        tracker.add_compliance_status(_make_status("ent-1", "reg-1", True))
        tracker.add_compliance_status(_make_status("ent-2", "reg-1", True))
        report = ComplianceReport(tracker)
        reg_report = report.generate_regulation_report("reg-1")
        assert reg_report["compliance_percentage"] == 100.0
