"""IntegratedSecurityManager cross-domain correlation tests (GS-224).

Characterizes the correlation-rule matching, cross-domain threat
correlation with synthetic component threats (orchestration threads are
never started), the broad error-swallowing behaviour of
_correlate_cross_domain_threat, incident lifecycle, and dashboard metrics.
"""

import logging
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from shapely.geometry import Point

from geo_infer_sec.core.cognitive_security import CognitiveThreat
from geo_infer_sec.core.digital_security import DigitalThreat, ThreatType
from geo_infer_sec.core.integrated_security import (
    IncidentSeverity,
    IntegratedSecurityManager,
    IntegratedThreat,
    SecurityDomain,
    ThreatCorrelationType,
)
from geo_infer_sec.core.physical_security import PhysicalThreat
from geo_infer_sec.models.security_models import (
    SecurityAlert,
    SecurityEventCategory,
    ThreatLevel,
)


@pytest.fixture
def manager() -> IntegratedSecurityManager:
    """IntegratedSecurityManager with orchestration threads never started."""
    return IntegratedSecurityManager()


def make_physical_threat(
    threat_type: str = "intrusion", severity: ThreatLevel = ThreatLevel.MEDIUM
) -> PhysicalThreat:
    """Build a synthetic physical threat not registered on any manager."""
    return PhysicalThreat(
        threat_id=f"phys-{uuid4().hex}",
        threat_type=threat_type,
        location=Point(5.0, 50.0),
        severity=severity,
        detected_at=datetime.now(),
        detection_method="unit-test",
        description="synthetic physical threat",
    )


def make_cognitive_threat(
    threat_type: str = "social_engineering",
) -> CognitiveThreat:
    """Build a synthetic cognitive threat not registered on any manager."""
    return CognitiveThreat(
        threat_id=f"cog-{uuid4().hex}",
        threat_type=threat_type,
        confidence_score=0.9,
        behavioral_indicators=["rapid_access_pattern"],
        prediction_model="unit-test-model",
        detection_method="unit-test",
        affected_entities=["user-1"],
        risk_score=0.8,
        recommended_actions=["review_access"],
    )


def seed_digital_threat(
    manager: IntegratedSecurityManager,
    threat_type: ThreatType = ThreatType.PHISHING,
) -> DigitalThreat:
    """Register a synthetic digital threat so correlation can find it."""
    threat = DigitalThreat(
        threat_id=f"dig-{uuid4().hex}",
        threat_type=threat_type,
        severity=ThreatLevel.HIGH,
        detected_at=datetime.now(),
        description="synthetic digital threat",
    )
    manager.digital_manager.active_threats[threat.threat_id] = threat
    return threat


def seed_cognitive_threat(
    manager: IntegratedSecurityManager,
    threat_type: str = "social_engineering",
) -> CognitiveThreat:
    """Register a synthetic cognitive threat so correlation can find it."""
    threat = make_cognitive_threat(threat_type)
    manager.cognitive_manager.cognitive_threats[threat.threat_id] = threat
    return threat


def trigger_multi_vector_threat(
    manager: IntegratedSecurityManager,
) -> IntegratedThreat:
    """Run a physical alert against seeded digital + cognitive threats.

    Seeds map onto the "Multi-Vector Attack" rule: physical
    surveillance_anomaly + digital phishing + cognitive social_engineering.
    """
    seed_digital_threat(manager, ThreatType.PHISHING)
    seed_cognitive_threat(manager, "social_engineering")
    primary = make_physical_threat("surveillance_anomaly", ThreatLevel.MEDIUM)
    manager._handle_physical_alert(primary)
    assert len(manager.integrated_threats) == 1
    return next(iter(manager.integrated_threats.values()))


class TestCorrelationRuleMatching:
    """The primary-domain rule match gates whether correlation runs."""

    def test_intrusion_matches_physical_breach_rule(self, manager):
        rule = manager.correlation_rules[0]  # "Physical Breach + Digital Access"
        threat = make_physical_threat("intrusion")
        assert (
            manager._matches_correlation_rule(
                SecurityDomain.PHYSICAL,
                threat,
                rule,
                datetime.now(),
                timedelta(minutes=30),
            )
            is True
        )

    def test_unrelated_physical_type_does_not_match(self, manager):
        rule = manager.correlation_rules[0]
        threat = make_physical_threat("surveillance_anomaly")
        assert (
            manager._matches_correlation_rule(
                SecurityDomain.PHYSICAL,
                threat,
                rule,
                datetime.now(),
                timedelta(minutes=30),
            )
            is False
        )

    def test_cognitive_payload_matches_by_type_value(self, manager):
        window = timedelta(minutes=30)
        behavioral_rule = manager.correlation_rules[1]
        social_rule = manager.correlation_rules[2]
        assert (
            manager._matches_correlation_rule(
                SecurityDomain.COGNITIVE,
                {"type": "behavioral_anomaly"},
                behavioral_rule,
                datetime.now(),
                window,
            )
            is True
        )
        assert (
            manager._matches_correlation_rule(
                SecurityDomain.COGNITIVE,
                {"type": "social_engineering"},
                social_rule,
                datetime.now(),
                window,
            )
            is True
        )
        assert (
            manager._matches_correlation_rule(
                SecurityDomain.COGNITIVE,
                {"type": "login_attempt"},
                behavioral_rule,
                datetime.now(),
                window,
            )
            is False
        )

    def test_cognitive_payload_without_type_is_unknown(self, manager):
        rule = manager.correlation_rules[1]
        assert (
            manager._matches_correlation_rule(
                SecurityDomain.COGNITIVE,
                {"unrelated": "payload"},
                rule,
                datetime.now(),
                timedelta(minutes=30),
            )
            is False
        )

    def test_domain_absent_from_rule_never_matches(self, manager):
        # The behavioral-anomaly rule has no "physical" conditions.
        rule = manager.correlation_rules[1]
        threat = make_physical_threat("intrusion")
        assert (
            manager._matches_correlation_rule(
                SecurityDomain.PHYSICAL,
                threat,
                rule,
                datetime.now(),
                timedelta(minutes=30),
            )
            is False
        )

    def test_threat_type_extraction_per_domain(self, manager):
        physical = make_physical_threat("intrusion")
        cognitive = {"type": "behavioral_anomaly"}
        digital = SecurityAlert(
            alert_id="alert-1",
            title="t",
            description="d",
            severity=ThreatLevel.MEDIUM,
            category=SecurityEventCategory.NETWORK_ACTIVITY,
        )
        assert (
            manager._extract_threat_type(SecurityDomain.PHYSICAL, physical)
            == "intrusion"
        )
        assert (
            manager._extract_threat_type(SecurityDomain.COGNITIVE, cognitive)
            == "behavioral_anomaly"
        )
        # SecurityAlert carries no threat_type attribute: extraction falls
        # back to "unknown" so a digital alert can never match a rule alone.
        assert (
            manager._extract_threat_type(SecurityDomain.DIGITAL, digital) == "unknown"
        )


class TestCrossDomainCorrelation:
    """End-to-end correlation over seeded component threats."""

    def test_multi_vector_attack_creates_integrated_threat(self, manager):
        threat = trigger_multi_vector_threat(manager)

        assert threat.correlation_type is ThreatCorrelationType.MULTI_DOMAIN
        assert set(threat.affected_domains) == {
            SecurityDomain.PHYSICAL,
            SecurityDomain.DIGITAL,
            SecurityDomain.COGNITIVE,
        }
        assert threat.combined_severity is IncidentSeverity.CRITICAL
        # Confidence: multi-domain base 0.75 + two correlations * 0.05.
        assert threat.confidence_score == pytest.approx(0.85)
        assert threat.attack_chain == [
            "physical: surveillance_anomaly",
            "digital: phishing",
            "cognitive: social_engineering",
        ]

    def test_unmatched_threat_produces_no_integrated_threat(self, manager):
        manager._handle_physical_alert(make_physical_threat("intrusion"))
        assert manager.integrated_threats == {}
        assert manager.security_incidents == {}

    def test_single_pair_correlation_is_temporal_and_not_escalated(self, manager):
        seed_cognitive_threat(manager)
        primary = make_physical_threat("surveillance_anomaly", ThreatLevel.MEDIUM)
        manager._handle_physical_alert(primary)

        assert len(manager.integrated_threats) == 1
        threat = next(iter(manager.integrated_threats.values()))
        assert threat.correlation_type is ThreatCorrelationType.TEMPORAL
        assert set(threat.affected_domains) == {
            SecurityDomain.PHYSICAL,
            SecurityDomain.COGNITIVE,
        }
        assert threat.combined_severity is IncidentSeverity.HIGH

        incident = next(iter(manager.security_incidents.values()))
        # HIGH severity is not auto-escalated: exactly the detection event.
        assert [entry["event"] for entry in incident.timeline] == [
            "Integrated threat detected"
        ]

    def test_correlation_error_is_swallowed_and_logged(self, manager, caplog):
        """A malformed component payload must not raise out of correlation.

        _find_matching_threats dereferences ``threat_type.value`` on digital
        threats; a threat carrying a plain string explodes there and the
        broad except in _correlate_cross_domain_threat contains it.
        """
        broken = DigitalThreat(
            threat_id="dig-broken",
            threat_type="phishing",  # type: ignore[arg-type]
            severity=ThreatLevel.HIGH,
            detected_at=datetime.now(),
        )
        manager.digital_manager.active_threats["dig-broken"] = broken
        primary = make_physical_threat("surveillance_anomaly", ThreatLevel.MEDIUM)

        with caplog.at_level(
            logging.ERROR, logger="geo_infer_sec.core.integrated_security"
        ):
            manager._handle_physical_alert(primary)

        assert "Error in threat correlation" in caplog.text
        assert manager.integrated_threats == {}

    def test_digital_alert_from_security_alert_model_never_correlates(self, manager):
        alert = SecurityAlert(
            alert_id="alert-1",
            title="Suspicious login",
            description="d",
            severity=ThreatLevel.HIGH,
            category=SecurityEventCategory.AUTHENTICATION,
        )
        manager._handle_digital_alert(alert)
        # SecurityAlert has no threat_type attribute, so the digital domain
        # extracts "unknown" and no rule can fire.
        assert manager.integrated_threats == {}

    def test_callbacks_on_domain_managers_are_wired(self, manager):
        assert manager._handle_physical_alert in (
            manager.physical_manager.alert_callbacks
        )
        assert manager._handle_digital_alert in (
            manager.digital_manager.alert_callbacks
        )
        assert manager._handle_cognitive_alert in (
            manager.cognitive_manager.alert_callbacks
        )


class TestResponseAndNotification:
    """Coordinated responses fan out to handlers and alert callbacks."""

    def test_response_handler_invoked_for_recommended_action(self, manager):
        calls = []
        manager.add_response_handler("Isolate affected digital systems", calls.append)
        threat = trigger_multi_vector_threat(manager)
        assert "Isolate affected digital systems" in threat.recommended_response
        assert len(calls) == 1
        assert calls[0] is threat

    def test_response_handler_error_does_not_break_correlation(self, manager):
        def broken_handler(threat):
            raise RuntimeError("handler exploded")

        manager.add_response_handler("Isolate affected digital systems", broken_handler)
        threat = trigger_multi_vector_threat(manager)
        assert threat.threat_id in manager.integrated_threats

    def test_alert_callback_receives_notification_data(self, manager):
        received = []
        manager.add_alert_callback(received.append)
        threat = trigger_multi_vector_threat(manager)

        assert len(received) == 1
        notification = received[0]
        assert notification["threat_id"] == threat.threat_id
        assert notification["severity"] == "critical"
        assert set(notification["affected_domains"]) == {
            "physical",
            "digital",
            "cognitive",
        }
        assert notification["attack_chain"] == threat.attack_chain

    def test_alert_callback_error_is_contained(self, manager):
        def exploding_callback(notification):
            raise RuntimeError("callback exploded")

        manager.add_alert_callback(exploding_callback)
        threat = trigger_multi_vector_threat(manager)
        assert threat.threat_id in manager.integrated_threats


class TestIncidentLifecycle:
    """Incidents are created from integrated threats and can be resolved."""

    def test_incident_created_from_correlation(self, manager):
        threat = trigger_multi_vector_threat(manager)

        incident_id = f"incident_{threat.threat_id}"
        incident = manager.security_incidents[incident_id]
        assert incident.status == "open"
        assert incident.severity is IncidentSeverity.CRITICAL
        assert set(incident.affected_systems) == {
            "physical",
            "digital",
            "cognitive",
        }
        assert incident.threat_vectors == threat.attack_chain
        # Auto-escalation is on by default and CRITICAL triggers it.
        assert [entry["event"] for entry in incident.timeline] == [
            "Integrated threat detected",
            "Incident escalated",
        ]
        assert [action["action"] for action in incident.response_actions] == (
            threat.recommended_response
        )

    def test_resolve_incident(self, manager):
        threat = trigger_multi_vector_threat(manager)
        incident_id = f"incident_{threat.threat_id}"

        assert manager.resolve_incident(incident_id, "handled by test") is True
        resolved = manager.security_incidents[incident_id]
        assert resolved.status == "resolved"
        assert resolved.resolved_at is not None
        assert resolved.timeline[-1]["details"] == "handled by test"
        assert manager.resolve_incident("incident_unknown", "") is False

    def test_get_security_incidents_filters_by_status(self, manager):
        threat = trigger_multi_vector_threat(manager)
        incident_id = f"incident_{threat.threat_id}"
        manager.resolve_incident(incident_id, "done")

        assert manager.get_security_incidents(status="open") == []
        assert [
            i.incident_id for i in manager.get_security_incidents(status="resolved")
        ] == [incident_id]
        assert len(manager.get_security_incidents()) == 1

    def test_stale_open_incident_auto_transitions_to_investigating(self, manager):
        from geo_infer_sec.core.integrated_security import SecurityIncident

        stale = SecurityIncident(
            incident_id="incident_stale",
            title="Stale incident",
            description="d",
            severity=IncidentSeverity.MEDIUM,
            status="open",
            affected_systems=["physical"],
            threat_vectors=[],
            timeline=[],
            response_actions=[],
            created_at=datetime.now() - timedelta(hours=25),
        )
        fresh = SecurityIncident(
            incident_id="incident_fresh",
            title="Fresh incident",
            description="d",
            severity=IncidentSeverity.MEDIUM,
            status="open",
            affected_systems=["physical"],
            threat_vectors=[],
            timeline=[],
            response_actions=[],
        )
        manager.security_incidents["incident_stale"] = stale
        manager.security_incidents["incident_fresh"] = fresh

        manager._update_incident_status()

        assert stale.status == "investigating"
        assert stale.timeline[-1]["event"] == "Status updated to investigating"
        assert fresh.status == "open"

    def test_cleanup_old_threats_removes_only_backdated_threats(self, manager):
        threat = trigger_multi_vector_threat(manager)
        threat.detected_at = datetime.now() - timedelta(days=8)
        manager._cleanup_old_threats()
        assert manager.integrated_threats == {}

        # A freshly correlated threat survives the same cleanup.
        trigger_multi_vector_threat(manager)
        manager._cleanup_old_threats()
        assert len(manager.integrated_threats) == 1


class TestDashboardAndMetrics:
    """Security score, dashboard shape, and metrics history."""

    def test_security_score_penalizes_active_threats(self, manager):
        for _ in range(3):
            threat = make_physical_threat("intrusion")
            manager.physical_manager.active_threats[threat.threat_id] = threat
        for _ in range(2):
            seed_cognitive_threat(manager)

        manager._update_security_posture()

        # 100 - (3 physical + 2 cognitive) * 5 + 85.0 baseline coverage * 0.1
        assert manager.security_metrics["overall_security_score"] == pytest.approx(83.5)
        assert "last_updated" in manager.security_metrics

    def test_dashboard_counts_active_threats(self, manager):
        physical_threat = make_physical_threat()
        manager.physical_manager.active_threats[physical_threat.threat_id] = (
            physical_threat
        )
        seed_digital_threat(manager)
        seed_cognitive_threat(manager)

        dashboard = manager.get_security_dashboard()

        assert dashboard["active_threats"] == {
            "physical": 1,
            "digital": 1,
            "cognitive": 1,
            "integrated": 0,
        }
        assert dashboard["open_incidents"] == 0
        assert set(dashboard["domain_status"]) == {
            "physical",
            "digital",
            "cognitive",
        }
        assert dashboard["domain_status"]["digital"] == "monitoring"

    def test_domain_status_thresholds(self, manager):
        assert manager._get_domain_status(SecurityDomain.DIGITAL) == "secure"

    def test_metrics_history_records_snapshot(self, manager):
        trigger_multi_vector_threat(manager)
        manager._collect_security_metrics()

        assert len(manager.performance_history) == 1
        snapshot = manager.performance_history[0]
        assert snapshot["integrated_threats"] == 1
        assert snapshot["open_incidents"] == 1
        assert snapshot["physical_security"]["active_threats"] == 0
        assert snapshot["digital_security"]["active_threats"] == 1

    def test_monitoring_lifecycle_flips_flags_without_threads(self, manager):
        # Simulate thread bookkeeping without actually starting threads.
        manager.orchestration_active = True
        manager.stop_integrated_monitoring()
        assert manager.orchestration_active is False
        assert manager.orchestration_threads == []
        assert manager.physical_manager.monitoring_active is False
        assert manager.digital_manager.monitoring_active is False
        assert manager.cognitive_manager.monitoring_active is False
