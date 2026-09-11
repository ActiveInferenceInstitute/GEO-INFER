"""Regression tests for the silent-fabrication fixes (GS-143/144/145)."""

from datetime import datetime, timedelta

from geo_infer_insurance.underwriting import (
    assess_risk,
    create_claims_processor,
    process_claim,
)
from geo_infer_insurance.underwriting.core.claims_processing import (
    ClaimStatus,
    ClaimsProcessingConfig,
)
from geo_infer_insurance.underwriting.models.underwriting_models import (
    UnderwritingQueue,
)


class TestLocationRiskRequiresInputs:
    """GS-143: no fabricated flood/coastal risk from hard-coded NYC anchors."""

    def test_sydney_coordinates_no_computed_flood_or_coastal_risk(self) -> None:
        application = {
            "property": {
                "latitude": -33.8688,
                "longitude": 151.2093,
                "value": 500000,
            }
        }
        result = assess_risk(application, "comprehensive")

        factors = result["location_analysis"]["risk_factors"]
        assert factors["flood_risk"] == "unavailable"
        assert factors["coastal_risk"] == "unavailable"
        assert "elevation_m" in result["location_analysis"]["reasons"]["flood_risk"]
        assert (
            "distance_to_water_km"
            in result["location_analysis"]["reasons"]["coastal_risk"]
        )

    def test_provided_elevation_and_water_distance_are_computed(self) -> None:
        application = {
            "property": {
                "latitude": -33.8688,
                "longitude": 151.2093,
                "elevation_m": 2.0,
                "distance_to_water_km": 3.0,
                "value": 500000,
            }
        }
        result = assess_risk(application, "comprehensive")

        factors = result["location_analysis"]["risk_factors"]
        assert factors["flood_risk"] == "high"
        assert factors["coastal_risk"] == "high"

    def test_missing_coordinates_do_not_default_to_nyc(self) -> None:
        application = {"property": {"value": 100000}}
        result = assess_risk(application, "comprehensive")

        assert "coordinates" not in result["location_analysis"]


class TestClaimsProcessorConfig:
    """GS-144: config dicts flow through the convenience wrapper."""

    def _claim_data(self) -> dict:
        return {
            "policy_id": "POL-001",
            "claim_type": "property_damage",
            "claimed_amount": 5000.0,
            "date_of_loss": "2026-01-15T10:00:00",
            "description": "Wind damage to roof",
            "cause_of_loss": "windstorm",
        }

    def test_wrapper_honors_manual_processing_mode(self) -> None:
        claim = process_claim(self._claim_data(), {"processing_mode": "manual"})
        assert claim.status == ClaimStatus.UNDER_REVIEW

    def test_create_claims_processor_accepts_config_object(self) -> None:
        config = ClaimsProcessingConfig()
        config.processing_mode = "manual"
        processor = create_claims_processor(config)
        claim = processor.process_claim(self._claim_data())
        assert claim.status == ClaimStatus.UNDER_REVIEW

    def test_create_claims_processor_rejects_unknown_fields(self) -> None:
        try:
            create_claims_processor({"no_such_field": 1})
        except ValueError as exc:
            assert "no_such_field" in str(exc)
        else:
            raise AssertionError("unknown config field must raise ValueError")

    def test_create_claims_processor_rejects_bad_types(self) -> None:
        try:
            create_claims_processor(42)
        except TypeError as exc:
            assert "config must be" in str(exc)
        else:
            raise AssertionError("non-dict config must raise TypeError")


class TestUnderwritingQueueWaitTimes:
    """GS-145: queue wait statistics track real case lifetimes."""

    def test_queued_then_removed_case_yields_nonzero_waits(self) -> None:
        queue = UnderwritingQueue(queue_id="q1", queue_type="standard")
        queue._case_enqueued_at["CASE-1"] = datetime.now() - timedelta(seconds=30)
        # enqueue through the API to keep total_pending consistent
        queue.total_pending += 1
        queue.average_wait_time = 0.0
        queue.longest_wait_time = 0.0

        assert queue.remove_from_queue("CASE-1") is True
        assert queue.average_wait_time >= 29.0
        assert queue.longest_wait_time >= 29.0

    def test_average_uses_completed_waits_denominator(self) -> None:
        queue = UnderwritingQueue(queue_id="q2", queue_type="standard")
        base = datetime.now()
        queue._case_enqueued_at["A"] = base - timedelta(seconds=10)
        queue._case_enqueued_at["B"] = base - timedelta(seconds=30)
        queue.total_pending = 2

        assert queue.remove_from_queue("A") is True
        assert queue.remove_from_queue("B") is True

        waits = [10.0, 30.0]
        expected_avg = sum(waits) / 2
        assert abs(queue.average_wait_time - expected_avg) < 1.0
        assert queue.longest_wait_time >= 30.0
        assert queue.total_pending == 0

    def test_remove_unknown_case_returns_false(self) -> None:
        queue = UnderwritingQueue(queue_id="q3", queue_type="standard")
        assert queue.remove_from_queue("MISSING") is False

    def test_duplicate_add_returns_false(self) -> None:
        queue = UnderwritingQueue(queue_id="q4", queue_type="standard")
        assert queue.add_to_queue("CASE-1") is True
        assert queue.add_to_queue("CASE-1") is False
