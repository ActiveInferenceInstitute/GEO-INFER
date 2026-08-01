"""
DOMAIN-02 Acceptance tests for GEO-INFER-NORMS documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. ComplianceTracker — threshold/range/boolean metric evaluation with weighted
   scoring, entity/regulation compliance lookup, no-metric handling.
2. NormativeInference — norm registration, observation-driven compliance
   checking, Bayesian compliance inference, prior-belief updates.
3. SocialNormDiffusion — network/spatial/content influence adoption
   probability (Jaccard similarity for content factor), step simulation.
4. LegalFramework — jurisdiction-regulation indexing and point lookups.
5. ZoningAnalyzer — compatibility matrix (same-category vs residential/
   industrial), point-in-district lookup.
6. Regulation / ZoningCode / Policy dataclass lifecycle (is_active, amend,
   use classification).

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import datetime
import uuid

import pytest
from shapely.geometry import Point, Polygon

from geo_infer_norms.core.compliance_tracking import ComplianceTracker
from geo_infer_norms.core.normative_inference import (
    NormativeInference,
    SocialNormDiffusion,
)
from geo_infer_norms.core.legal_frameworks import LegalFramework
from geo_infer_norms.core.zoning_analysis import ZoningAnalyzer
from geo_infer_norms.models.compliance_status import ComplianceStatus, ComplianceMetric
from geo_infer_norms.models.legal_entity import LegalEntity, Jurisdiction
from geo_infer_norms.models.regulation import Regulation
from geo_infer_norms.models.zoning import ZoningCode, ZoningDistrict


# ---------------------------------------------------------------------------
# ComplianceTracker
# ---------------------------------------------------------------------------

class TestComplianceTrackerAcceptance:
    """Acceptance: threshold/range/boolean evaluation and weighted scoring."""

    def _threshold_metric(self, reg_id: str = "reg-air") -> ComplianceMetric:
        return ComplianceMetric.create(
            name="air_quality",
            description="PM2.5 threshold",
            regulation_id=reg_id,
            evaluation_type="threshold",
            primary_field="pm25",
            required_fields=["pm25"],
            threshold_value=35,
            comparison="less_than",
        )

    def _entity(self, ent_id: str = "facility-1") -> LegalEntity:
        return LegalEntity(id=ent_id, name="Facility 1", entity_type="facility")

    def _regulation(self, reg_id: str = "reg-air") -> Regulation:
        return Regulation(
            id=reg_id, name="Air Quality", description="PM2.5 limit",
            regulation_type="environmental", issuing_authority="County",
            effective_date=datetime.date(2026, 1, 1),
        )

    def test_threshold_less_than_compliant_when_value_is_low(self):
        """A value below a less_than threshold yields full compliance."""
        metric = self._threshold_metric()
        tracker = ComplianceTracker("environmental", compliance_metrics=[metric])
        status = tracker.evaluate_compliance(self._entity(), self._regulation(), {"pm25": 28})
        assert status.is_compliant is True
        assert status.compliance_level == 1.0
        assert len(tracker.compliance_statuses) == 1
        assert status.metric_results[0]["is_compliant"] is True

    def test_threshold_less_than_noncompliant_when_value_is_high(self):
        """A value above a less_than threshold yields non-compliance."""
        metric = self._threshold_metric()
        tracker = ComplianceTracker("environmental", compliance_metrics=[metric])
        status = tracker.evaluate_compliance(self._entity(), self._regulation(), {"pm25": 40})
        assert status.is_compliant is False
        assert status.compliance_level == 0.0

    def test_range_evaluation_partial_outside(self):
        """A value outside a range metric reports a sub-1.0 compliance level."""
        metric = ComplianceMetric.create(
            name="temp_range",
            description="Operating temperature range",
            regulation_id="reg-temp",
            evaluation_type="range",
            primary_field="temperature",
            required_fields=["temperature"],
            range_min=10.0,
            range_max=30.0,
            weight=2.0,
        )
        tracker = ComplianceTracker("ops", compliance_metrics=[metric])
        reg = Regulation(
            id="reg-temp", name="Temperature", description="Temp range",
            regulation_type="safety", issuing_authority="Plant",
            effective_date=datetime.date(2026, 1, 1),
        )
        # Value 35 is above max 30 → non-compliant, level reflects distance.
        status = tracker.evaluate_compliance(self._entity(), reg, {"temperature": 35})
        assert status.is_compliant is False
        assert 0.0 <= status.compliance_level < 1.0

    def test_boolean_evaluation_true(self):
        """A boolean metric with a truthy field value is compliant."""
        metric = ComplianceMetric.create(
            name="has_permit",
            description="Permit on file",
            regulation_id="reg-permit",
            evaluation_type="boolean",
            primary_field="permit_present",
            required_fields=["permit_present"],
        )
        tracker = ComplianceTracker("admin", compliance_metrics=[metric])
        reg = Regulation(
            id="reg-permit", name="Permit", description="Permit required",
            regulation_type="administrative", issuing_authority="City",
            effective_date=datetime.date(2026, 1, 1),
        )
        status = tracker.evaluate_compliance(self._entity(), reg, {"permit_present": True})
        assert status.is_compliant is True
        assert status.compliance_level == 1.0

    def test_no_metrics_yields_non_compliant_status(self):
        """Evaluating against a regulation with no registered metrics returns non-compliant."""
        tracker = ComplianceTracker("empty")
        reg = self._regulation()
        status = tracker.evaluate_compliance(self._entity(), reg, {"pm25": 28})
        assert status.is_compliant is False
        assert status.compliance_level == 0.0
        assert "No compliance metrics" in status.notes

    def test_entity_compliance_lookup_aggregates(self):
        """get_entity_compliance summarizes compliant/non-compliant counts."""
        metric = self._threshold_metric()
        tracker = ComplianceTracker("env", compliance_metrics=[metric])
        entity = self._entity()
        reg = self._regulation()
        # First: non-compliant (pm25 too high), then compliant.
        tracker.evaluate_compliance(entity, reg, {"pm25": 40})
        tracker.evaluate_compliance(entity, reg, {"pm25": 28})
        report = tracker.get_entity_compliance(entity.id)
        assert report["entity_id"] == entity.id
        # The most recent status per regulation is the compliant one.
        assert report["compliance_count"] >= 1
        assert report["status"] == "compliant"

    def test_entity_compliance_unknown_returns_unknown(self):
        """An entity with no records returns an 'unknown' status."""
        tracker = ComplianceTracker("env")
        report = tracker.get_entity_compliance("ghost")
        assert report["status"] == "unknown"
        assert report["compliance_count"] == 0


# ---------------------------------------------------------------------------
# NormativeInference
# ---------------------------------------------------------------------------

class TestNormativeInferenceAcceptance:
    """Acceptance: norm registration and Bayesian compliance inference."""

    @pytest.fixture
    def inference(self) -> NormativeInference:
        ni = NormativeInference()
        ni.add_norm(
            name="Speed Limit",
            condition=lambda obs: obs.get("speed", float("inf")) <= 50.0,
            probability=0.9,
            description="Urban speed limit",
        )
        return ni

    def test_add_norm_returns_unique_id(self, inference):
        """Each added norm gets a distinct UUID."""
        first = list(inference.norms.keys())[0]
        assert first in inference.norms
        second = inference.add_norm(
            name="Helmet", condition=lambda obs: obs.get("helmet", False) is True,
        )
        assert second != first
        assert len(inference.norms) == 2

    def test_check_norm_compliant_observation(self, inference):
        """An observation within the speed limit is reported compliant with certainty 1.0."""
        norm_id = list(inference.norms.keys())[0]
        inference.add_observation("cyclist1", "speed", 40.0, certainty=1.0)
        compliant, certainty = inference.check_norm_compliance(norm_id, "cyclist1")
        assert compliant is True
        assert certainty == 1.0

    def test_check_norm_violating_observation(self, inference):
        """An observation above the speed limit is non-compliant."""
        norm_id = list(inference.norms.keys())[0]
        inference.add_observation("cyclist2", "speed", 70.0, certainty=1.0)
        compliant, certainty = inference.check_norm_compliance(norm_id, "cyclist2")
        assert compliant is False

    def test_check_norm_no_observations_is_uncertain(self, inference):
        """With no observations, compliance is reported False with 0.0 certainty."""
        norm_id = list(inference.norms.keys())[0]
        compliant, certainty = inference.check_norm_compliance(norm_id, "nobody")
        assert compliant is False
        assert certainty == 0.0

    def test_infer_compliance_single_norm_uses_prior(self, inference):
        """Bayesian inference combines observation certainty with a prior belief."""
        norm_id = list(inference.norms.keys())[0]
        inference.set_prior_belief(norm_id, "cyclist1", 0.8)
        inference.add_observation("cyclist1", "speed", 40.0, certainty=0.9)
        probability = inference.infer_compliance("cyclist1", norm_id)
        # A compliant high-certainty observation over a 0.8 prior pushes probability up.
        assert probability > 0.8

    def test_infer_compliance_all_norms_returns_dict(self, inference):
        """Inferring without a specific norm returns a per-norm mapping."""
        norm_id = list(inference.norms.keys())[0]
        inference.add_observation("cyclist1", "speed", 40.0, certainty=1.0)
        result = inference.infer_compliance("cyclist1")
        assert isinstance(result, dict)
        assert norm_id in result

    def test_unknown_norm_returns_zero(self, inference):
        """Inferring compliance for an unknown norm returns 0.0."""
        assert inference.infer_compliance("cyclist1", "no-such-norm") == 0.0


# ---------------------------------------------------------------------------
# SocialNormDiffusion
# ---------------------------------------------------------------------------

class TestSocialNormDiffusionAcceptance:
    """Acceptance: norm adoption via network/spatial/content factors."""

    def test_network_influence_adoption(self):
        """A non-adopter connected to adopters reaches threshold and adopts."""
        model = SocialNormDiffusion()
        for eid in ("a", "b", "c"):
            model.add_entity(eid, attributes={}, adoption_threshold=0.5)
        model.add_norm("n1", "Recycle", initial_adopters=["a", "b"],
                       spatial_factor=0.0, network_factor=1.0)
        model.add_social_connection("a", "c", strength=1.0)
        model.add_social_connection("b", "c", strength=1.0)
        # c is connected to two adopters out of two → network_influence = 1.0.
        prob = model.calculate_adoption_probability("n1", "c")
        assert prob == 1.0
        # A simulation step should flip c to adopted.
        step = model.simulate_step()
        assert "c" in step["norm_changes"]["n1"]

    def test_content_influence_uses_jaccard(self):
        """Content factor adoption uses Jaccard similarity over attribute keys."""
        model = SocialNormDiffusion()
        model.add_entity("e1", attributes={"env", "climate"}, adoption_threshold=0.0)
        model.add_entity("e2", attributes={"env"}, adoption_threshold=0.0)
        # Norm attributes overlap 'env' with e1 (intersection 1, union 2 → 0.5)
        # and fully overlap with e2 (intersection 1, union 1 → 1.0).
        model.add_norm("n1", "Green", initial_adopters=[],
                       spatial_factor=0.0, network_factor=0.0, content_factor=1.0,
                       attributes={"env"})
        prob_e1 = model.calculate_adoption_probability("n1", "e1")
        prob_e2 = model.calculate_adoption_probability("n1", "e2")
        assert prob_e2 == 1.0  # full overlap
        assert prob_e1 == 0.5  # half overlap

    def test_adoption_summary_counts(self):
        """The adoption summary reports adopted/total per norm."""
        model = SocialNormDiffusion()
        for eid in ("a", "b", "c"):
            model.add_entity(eid, attributes={})
        model.add_norm("n1", "Norm", initial_adopters=["a", "b"])
        summary = model.get_adoption_summary()
        assert summary["n1"]["adopted_count"] == 2
        assert summary["n1"]["total_count"] == 3
        assert summary["n1"]["adoption_rate"] == round(2 / 3, 4) if summary["n1"]["total_count"] else 0


# ---------------------------------------------------------------------------
# LegalFramework
# ---------------------------------------------------------------------------

class TestLegalFrameworkAcceptance:
    """Acceptance: jurisdiction-regulation indexing and point lookups."""

    def test_get_regulations_by_jurisdiction(self):
        """A regulation tagged with a jurisdiction is returned by jurisdiction lookup."""
        jur = Jurisdiction(id="j1", name="County", level="county")
        reg = Regulation(
            id="r1", name="Buffer", description="Riparian buffer",
            regulation_type="environmental", issuing_authority="County",
            effective_date=datetime.date(2020, 1, 1),
            applicable_jurisdictions=["j1"],
        )
        lf = LegalFramework("Env", jurisdictions=[jur], regulations=[reg])
        applicable = lf.get_regulations_by_jurisdiction("j1")
        assert reg.id == applicable[0].id

    def test_unknown_jurisdiction_returns_empty(self):
        """An unregistered jurisdiction yields no regulations."""
        lf = LegalFramework("Env")
        assert lf.get_regulations_by_jurisdiction("nope") == []

    def test_get_jurisdictions_by_point(self):
        """Point lookup returns jurisdictions whose geometry contains the point."""
        poly = Polygon([(0, 0), (0, 10), (10, 10), (10, 0)])
        jur = Jurisdiction(id="j1", name="Zone", level="city", geometry=poly)
        lf = LegalFramework("Env", jurisdictions=[jur])
        inside = lf.get_jurisdictions_by_point(Point(5, 5))
        outside = lf.get_jurisdictions_by_point(Point(20, 20))
        assert jur.id == inside[0].id
        assert outside == []


# ---------------------------------------------------------------------------
# ZoningAnalyzer
# ---------------------------------------------------------------------------

class TestZoningAnalyzerAcceptance:
    """Acceptance: zoning compatibility matrix and point lookups."""

    def _codes(self):
        return [
            ZoningCode(code="R-1", name="Residential", description="Single family",
                       category="residential", jurisdiction_id="j1"),
            ZoningCode(code="I-1", name="Industrial", description="Light industrial",
                       category="industrial", jurisdiction_id="j1"),
        ]

    def test_same_code_fully_compatible(self):
        """Identical zoning codes are fully compatible (score 1.0)."""
        analyzer = ZoningAnalyzer(zoning_codes=self._codes())
        assert analyzer.calculate_compatibility("R-1", "R-1") == 1.0

    def test_residential_industrial_incompatible(self):
        """Residential and industrial codes receive the low compatibility score."""
        analyzer = ZoningAnalyzer(zoning_codes=self._codes())
        assert analyzer.calculate_compatibility("R-1", "I-1") == 0.1

    def test_unknown_code_defaults_to_medium(self):
        """Unknown code pairs fall back to the default medium compatibility (0.5)."""
        analyzer = ZoningAnalyzer(zoning_codes=self._codes())
        assert analyzer.calculate_compatibility("R-1", "Mystery") == 0.5

    def test_point_in_district_lookup(self):
        """get_zoning_at_point returns districts whose geometry contains the point."""
        poly = Polygon([(0, 0), (0, 10), (10, 10), (10, 0)])
        district = ZoningDistrict(id="d1", name="Downtown", zoning_code="R-1",
                                  jurisdiction_id="j1", geometry=poly)
        analyzer = ZoningAnalyzer(zoning_districts=[district])
        hits = analyzer.get_zoning_at_point(Point(5, 5))
        assert len(hits) == 1
        assert hits[0].id == "d1"
        assert analyzer.get_zoning_at_point(Point(20, 20)) == []


# ---------------------------------------------------------------------------
# Regulation / Policy lifecycle
# ---------------------------------------------------------------------------

class TestRegulationLifecycleAcceptance:
    """Acceptance: regulation active/inactive and amendment lifecycle."""

    def test_is_active_within_window(self):
        """A regulation is active between effective and expiration dates."""
        reg = Regulation(
            id="r1", name="Rule", description="A rule",
            regulation_type="safety", issuing_authority="City",
            effective_date=datetime.date(2020, 1, 1),
            expiration_date=datetime.date(2030, 12, 31),
        )
        assert reg.is_active(datetime.date(2025, 6, 1)) is True
        assert reg.is_active(datetime.date(2019, 1, 1)) is False  # before effective
        assert reg.is_active(datetime.date(2031, 1, 1)) is False  # after expiration

    def test_amend_updates_description_and_date(self):
        """Amending a regulation replaces its description and records the date."""
        reg = Regulation(
            id="r1", name="Rule", description="Original",
            regulation_type="safety", issuing_authority="City",
            effective_date=datetime.date(2020, 1, 1),
        )
        amend_date = datetime.date(2025, 3, 15)
        reg.amend("Revised text", amendment_date=amend_date)
        assert reg.description == "Revised text"
        assert reg.amendment_date == amend_date

    def test_zoning_code_use_classification(self):
        """ZoningCode classifies allowed/conditional/prohibited uses."""
        code = ZoningCode.create(
            code="M-1", name="Mixed", description="Mixed use",
            category="mixed_use", jurisdiction_id="j1",
            allowed_uses=["residential", "retail"],
            conditional_uses=["office"],
            prohibited_uses=["heavy_industry"],
        )
        assert code.is_use_allowed("residential") is True
        assert code.is_use_conditional("office") is True
        assert code.is_use_prohibited("heavy_industry") is True
        # An unlisted use is prohibited when explicit prohibited_uses exist.
        assert code.is_use_prohibited("nuclear") is True
