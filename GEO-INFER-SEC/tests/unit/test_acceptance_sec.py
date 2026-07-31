"""
DOMAIN-01 Acceptance tests for GEO-INFER-SEC documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. DigitalSecurityManager threat detection — SQL injection, XSS, DDoS,
   data exfiltration, unauthorized access pattern detection.
2. CognitiveSecurityManager behavioral profiling — analyze_user_behavior,
   anomaly detection, behavior deviation scoring.
3. RiskAssessment / GeospatialSecurityRisk — risk scoring, filtering,
   serialization round-trip.
4. ComplianceFramework — rule management, compliance checking, violations.
5. SecurityFramework — secure_data_processing with spatial anonymization.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from geo_infer_sec.core.digital_security import DigitalSecurityManager, ThreatType
from geo_infer_sec.core.cognitive_security import (
    CognitiveSecurityManager,
    BehaviorType,
)
from geo_infer_sec.models.security_models import (
    SecurityEvent,
    SecurityEventCategory,
    ThreatLevel,
    SecurityAlert,
)
from geo_infer_sec.models.risk_assessment import (
    RiskAssessment,
    GeospatialSecurityRisk,
    RiskSeverity,
    RiskLikelihood,
    RiskCategory,
)
from geo_infer_sec.core.compliance import (
    ComplianceFramework,
    ComplianceRule,
    ComplianceRegime,
)
from geo_infer_sec import SecurityFramework


# ---------------------------------------------------------------------------
# DigitalSecurityManager threat detection
# ---------------------------------------------------------------------------

class TestDigitalThreatDetection:
    """Acceptance: the digital security manager classifies real threats."""

    @pytest.fixture
    def manager(self) -> DigitalSecurityManager:
        return DigitalSecurityManager()

    def test_sql_injection_detected(self, manager):
        """SQL injection patterns in request_data are flagged."""
        assert manager._detect_sql_injection("' OR 1=1 --") is True
        assert manager._detect_sql_injection("UNION SELECT * FROM users") is True
        assert manager._detect_sql_injection("DROP TABLE accounts") is True

    def test_sql_injection_benign_not_flagged(self, manager):
        """Normal queries are not flagged as SQL injection."""
        assert manager._detect_sql_injection("SELECT name FROM products") is False
        assert manager._detect_sql_injection("hello world") is False

    def test_xss_detected(self, manager):
        """XSS patterns in request_data are flagged."""
        assert manager._detect_xss("<script>alert(1)</script>") is True
        assert manager._detect_xss("javascript:void(0)") is True
        assert manager._detect_xss('<img src=x onerror="evil()">') is True

    def test_xss_benign_not_flagged(self, manager):
        """Normal HTML-like content is not flagged as XSS."""
        assert manager._detect_xss("normal text content") is False

    def test_data_exfiltration_large_volume(self, manager):
        """Data volume above 100 MB threshold triggers exfiltration flag."""
        assert manager._detect_data_exfiltration({"data_volume": 200 * 1024 * 1024}) is True

    def test_data_exfiltration_normal_volume(self, manager):
        """Normal data volume does not trigger exfiltration."""
        assert manager._detect_data_exfiltration({"data_volume": 1024}) is False

    def test_classify_sql_injection(self, manager):
        """_classify_threat returns SQL_INJECTION for injection payloads."""
        result = manager._classify_threat({"request_data": "'; DROP TABLE users; --"})
        assert result == ThreatType.SQL_INJECTION

    def test_classify_xss(self, manager):
        """_classify_threat returns XSS for script payloads."""
        result = manager._classify_threat({"request_data": "<script>evil()</script>"})
        assert result == ThreatType.XSS

    def test_classify_login_failure(self, manager):
        """_classify_threat returns UNAUTHORIZED_ACCESS for login failures."""
        result = manager._classify_threat({"event_type": "login_failure"})
        assert result == ThreatType.UNAUTHORIZED_ACCESS

    def test_classify_benign_returns_none(self, manager):
        """_classify_threat returns None for benign events."""
        result = manager._classify_threat({"request_data": "hello", "event_type": "api_call"})
        assert result is None

    def test_detect_threat_stores_in_active_threats(self, manager):
        """detect_threat stores detected threats and fires an alert.

        The SecurityAlert constructor mismatch in _trigger_alert was fixed
        (alert_id/title/description/category, no invalid threat_id/message).
        """
        alert_callback_calls = []

        def on_alert(alert):
            alert_callback_calls.append(alert)

        manager.alert_callbacks.append(on_alert)
        threat = manager.detect_threat({
            "event_type": "login_failure",
            "source_ip": "10.0.0.99",
        })
        assert len(manager.active_threats) >= 1
        stored = list(manager.active_threats.values())[0]
        assert stored.threat_type == ThreatType.UNAUTHORIZED_ACCESS
        # The alert callback fires with a properly constructed SecurityAlert.
        assert len(alert_callback_calls) == 1
        alert = alert_callback_calls[0]
        assert alert.alert_id == f"alert_{threat.threat_id}"
        assert alert.title
        assert alert.description
        assert alert.severity == stored.severity


# ---------------------------------------------------------------------------
# CognitiveSecurityManager behavioral profiling
# ---------------------------------------------------------------------------

class TestCognitiveSecurityManager:
    """Acceptance: behavioral profiling and anomaly detection."""

    @pytest.fixture
    def manager(self) -> CognitiveSecurityManager:
        return CognitiveSecurityManager()

    def _make_events(self, count: int = 10, event_type: str = "login_success") -> list:
        now = datetime.now()
        return [
            SecurityEvent(
                event_id=f"e{i}",
                event_type=event_type,
                category=SecurityEventCategory.AUTHENTICATION,
                timestamp=now - timedelta(hours=i),
                metadata={"source_ip": "192.168.1.1", "data_volume": 100},
            )
            for i in range(count)
        ]

    def test_analyze_behavior_returns_profile(self, manager):
        """analyze_user_behavior returns a BehaviorProfile for valid events."""
        events = self._make_events(10)
        profile = manager.analyze_user_behavior("user1", events)
        assert profile.entity_id == "user1"
        assert profile.entity_type == "user"

    def test_analyze_behavior_baseline_is_normal(self, manager):
        """First-time users get a NORMAL behavior classification."""
        events = self._make_events(5)
        profile = manager.analyze_user_behavior("new_user", events)
        assert profile.behavior_type == BehaviorType.NORMAL
        assert profile.behavior_score == 0.0

    def test_analyze_behavior_empty_events(self, manager):
        """Empty event list returns an empty profile."""
        profile = manager.analyze_user_behavior("nobody", [])
        assert profile.entity_id == "nobody"
        assert profile.behavior_type == BehaviorType.NORMAL

    def test_behavior_metrics_extracted(self, manager):
        """Behavioral metrics are computed from events."""
        events = self._make_events(10)
        metrics = manager._extract_behavioral_metrics(events)
        assert "login_frequency" in metrics
        assert "failed_login_rate" in metrics
        assert "unique_source_ips" in metrics
        assert metrics["login_frequency"] > 0.0

    def test_unusual_hour_activity_calculated(self, manager):
        """Events at unusual hours (22:00-06:00) are counted."""
        # Create an event at 2 AM
        late_event = SecurityEvent(
            event_id="late",
            event_type="login_success",
            category=SecurityEventCategory.AUTHENTICATION,
            timestamp=datetime.now().replace(hour=2, minute=0),
            metadata={"source_ip": "10.0.0.1"},
        )
        day_event = SecurityEvent(
            event_id="day",
            event_type="login_success",
            category=SecurityEventCategory.AUTHENTICATION,
            timestamp=datetime.now().replace(hour=14, minute=0),
            metadata={"source_ip": "10.0.0.2"},
        )
        ratio = manager._calculate_unusual_hour_activity([late_event, day_event])
        assert ratio == 0.5

    def test_behavior_deviation_zero_for_identical(self, manager):
        """Identical baseline and current metrics yield zero deviation."""
        metrics = {"a": 1.0, "b": 2.0}
        deviation = manager._calculate_behavior_deviation(metrics, metrics)
        assert deviation == 0.0

    def test_behavior_deviation_nonzero_for_different(self, manager):
        """Different metrics yield positive deviation."""
        baseline = {"a": 1.0}
        current = {"a": 2.0}
        deviation = manager._calculate_behavior_deviation(baseline, current)
        assert deviation > 0.0


# ---------------------------------------------------------------------------
# RiskAssessment / GeospatialSecurityRisk
# ---------------------------------------------------------------------------

class TestRiskAssessment:
    """Acceptance: risk scoring, filtering, and serialization."""

    @pytest.fixture
    def high_risk(self) -> GeospatialSecurityRisk:
        return GeospatialSecurityRisk(
            name="Data Breach",
            description="Database exposure risk",
            category=RiskCategory.DATA_BREACH,
            severity=RiskSeverity.HIGH,
            likelihood=RiskLikelihood.LIKELY,
            affected_asset="user_db",
            mitigation_strategies=["encrypt", "audit"],
        )

    @pytest.fixture
    def low_risk(self) -> GeospatialSecurityRisk:
        return GeospatialSecurityRisk(
            name="Privacy",
            description="Minor privacy concern",
            category=RiskCategory.PRIVACY,
            severity=RiskSeverity.LOW,
            likelihood=RiskLikelihood.RARE,
            affected_asset="location_log",
        )

    def test_risk_score_high_risk_higher(self, high_risk, low_risk):
        """HIGH severity × LIKELY likelihood > LOW severity × RARE likelihood."""
        assert high_risk.calculate_risk_score() > low_risk.calculate_risk_score()

    def test_risk_score_values(self, high_risk, low_risk):
        """Score = severity × likelihood per the documented mapping."""
        assert high_risk.calculate_risk_score() == 3 * 4  # HIGH=3, LIKELY=4
        assert low_risk.calculate_risk_score() == 1 * 1   # LOW=1, RARE=1

    def test_risk_to_dict_round_trip(self, high_risk):
        """to_dict → from_dict preserves the risk."""
        d = high_risk.to_dict()
        assert d["name"] == "Data Breach"
        assert d["risk_score"] == 12
        restored = GeospatialSecurityRisk.from_dict(d)
        assert restored.name == high_risk.name
        assert restored.calculate_risk_score() == high_risk.calculate_risk_score()

    def test_assessment_add_and_total(self, high_risk, low_risk):
        """RiskAssessment aggregates scores correctly."""
        assessment = RiskAssessment("Sec Audit", "Annual review")
        assessment.add_risk(high_risk)
        assessment.add_risk(low_risk)
        assert assessment.calculate_total_risk_score() == 12 + 1

    def test_assessment_remove_risk(self, high_risk, low_risk):
        """Removing a risk reduces the total."""
        assessment = RiskAssessment("Audit")
        assessment.add_risk(high_risk)
        assessment.add_risk(low_risk)
        assert assessment.remove_risk("Privacy") is True
        assert assessment.remove_risk("Nonexistent") is False
        assert len(assessment.risks) == 1

    def test_assessment_filter_by_category(self, high_risk, low_risk):
        """get_risks_by_category returns only matching risks."""
        assessment = RiskAssessment("Audit")
        assessment.add_risk(high_risk)
        assessment.add_risk(low_risk)
        privacy = assessment.get_risks_by_category(RiskCategory.PRIVACY)
        assert len(privacy) == 1
        assert privacy[0].name == "Privacy"

    def test_assessment_highest_risks(self, high_risk, low_risk):
        """get_highest_risks returns risks sorted by score descending."""
        assessment = RiskAssessment("Audit")
        assessment.add_risk(low_risk)
        assessment.add_risk(high_risk)
        top = assessment.get_highest_risks(1)
        assert len(top) == 1
        assert top[0].name == "Data Breach"

    def test_assessment_to_dict(self, high_risk, low_risk):
        """Assessment serialization includes all risks and total score."""
        assessment = RiskAssessment("Audit", "desc")
        assessment.add_risk(high_risk)
        assessment.add_risk(low_risk)
        d = assessment.to_dict()
        assert d["name"] == "Audit"
        assert d["total_risk_score"] == 13
        assert len(d["risks"]) == 2


# ---------------------------------------------------------------------------
# ComplianceFramework
# ---------------------------------------------------------------------------

class TestComplianceFramework:
    """Acceptance: compliance rule management and checking."""

    @pytest.fixture
    def framework(self) -> ComplianceFramework:
        cf = ComplianceFramework()
        cf.add_rule(ComplianceRule(
            name="no_null_coords",
            regime=ComplianceRegime.GDPR,
            description="Coordinates must not be null",
            validator=lambda data: data is not None,
            priority=2,
        ))
        cf.add_rule(ComplianceRule(
            name="must_be_dict",
            regime=ComplianceRegime.GDPR,
            description="Data must be a dict",
            validator=lambda data: isinstance(data, dict),
            priority=1,
        ))
        cf.add_rule(ComplianceRule(
            name="hipaa_check",
            regime=ComplianceRegime.HIPAA,
            description="PHI must be encrypted",
            validator=lambda data: True,
        ))
        return cf

    def test_get_rules_by_regime(self, framework):
        """get_rules_by_regime filters correctly."""
        gdpr_rules = framework.get_rules_by_regime(ComplianceRegime.GDPR)
        assert len(gdpr_rules) == 2
        hipaa_rules = framework.get_rules_by_regime(ComplianceRegime.HIPAA)
        assert len(hipaa_rules) == 1

    def test_check_compliance_passes_valid_data(self, framework):
        """Valid data produces no violations."""
        violations = framework.check_compliance({"key": "value"}, "ref1")
        assert len(violations) == 0

    def test_check_compliance_fails_invalid_data(self, framework):
        """Non-dict data triggers the must_be_dict violation."""
        violations = framework.check_compliance("not_a_dict", "ref2")
        assert len(violations) >= 1
        assert any(v.rule.name == "must_be_dict" for v in violations)

    def test_check_compliance_filtered_by_regime(self, framework):
        """Filtering by regime only checks rules in that regime."""
        violations = framework.check_compliance(
            "invalid", "ref3", regimes=[ComplianceRegime.HIPAA]
        )
        assert len(violations) == 0  # HIPAA rule always passes

    def test_violation_to_dict(self, framework):
        """Violations serialize to dict correctly."""
        violations = framework.check_compliance("bad", "ref4")
        assert len(violations) >= 1
        d = violations[0].to_dict()
        assert "rule_name" in d
        assert "regime" in d
        assert "data_reference" in d

    def test_rule_check_catches_exceptions(self):
        """A validator that raises returns False (not an exception)."""
        rule = ComplianceRule(
            name="bad_validator",
            regime=ComplianceRegime.GDPR,
            description="Always fails",
            validator=lambda data: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        assert rule.check("test") is False


# ---------------------------------------------------------------------------
# SecurityFramework (high-level)
# ---------------------------------------------------------------------------

class TestSecurityFramework:
    """Acceptance: the high-level SecurityFramework data protection."""

    def test_secure_data_processing_anonymizes_coordinates(self):
        """secure_data_processing anonymizes lat/lon columns."""
        sf = SecurityFramework()
        df = pd.DataFrame({
            "lat": [40.7128, 34.0522],
            "lon": [-74.0060, -118.2437],
            "value": [1, 2],
        })
        protected = sf.secure_data_processing(df, privacy_level="standard")
        assert protected.shape == df.shape
        # Lat/lon should be modified (rounded precision)
        assert not protected["lat"].equals(df["lat"])

    def test_secure_data_processing_records_audit(self):
        """secure_data_processing records an audit event."""
        sf = SecurityFramework()
        df = pd.DataFrame({"lat": [40.0], "lon": [-74.0], "val": [1]})
        sf.secure_data_processing(df, privacy_level="high")
        assert len(sf.audit_log) >= 1
        event = sf.audit_log[-1]
        assert event["user_id"] == "system"
        assert "privacy_level" in event["data_access"]

    def test_invalid_privacy_level_raises(self):
        """An unsupported privacy level raises ValueError."""
        sf = SecurityFramework()
        df = pd.DataFrame({"lat": [40.0], "lon": [-74.0]})
        with pytest.raises(ValueError, match="Unsupported privacy level"):
            sf.secure_data_processing(df, privacy_level="maximum")

    def test_audit_access_returns_event(self):
        """audit_access returns the recorded event."""
        sf = SecurityFramework()
        event = sf.audit_access("user42", {"operation": "read"})
        assert event["user_id"] == "user42"
        assert event["status"] == "recorded"
        assert "timestamp" in event
        assert len(sf.audit_log) == 1
