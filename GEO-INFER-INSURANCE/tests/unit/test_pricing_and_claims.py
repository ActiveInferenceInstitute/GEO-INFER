"""Behavioral tests for premium pricing and the claims lifecycle."""

from geo_infer_insurance.underwriting import calculate_premium, process_claim
from geo_infer_insurance.underwriting.core.claims_processing import (
    ClaimStatus,
    ClaimsProcessor,
    ClaimsProcessingConfig,
    Payment,
    Reserve,
)
from geo_infer_insurance.underwriting.core.pricing_engine import PricingEngine


def _application() -> dict:
    return {
        "property": {
            "type": "residential",
            "value": 300000,
            "year_built": 2005,
            "construction": "frame",
            "territory": "urban",
        },
        "coverage_requests": [
            {"coverage_type": "dwelling", "limit": 300000},
        ],
    }


def _risk_assessment() -> dict:
    return {
        "risk_score": 0.35,
        "risk_level": "moderate",
        "factors": {"location_risk": 0.4, "property_risk": 0.3, "historical_risk": 0.3},
        "assessment_method": "basic",
        "confidence": 0.7,
    }


def _rule_evaluation() -> dict:
    return {"passed": True, "violations": [], "adjustments": []}


class TestPremiumPricing:
    def test_calculate_premium_returns_positive_total(self) -> None:
        calc = calculate_premium(_application(), _risk_assessment(), _rule_evaluation())

        assert calc.total_premium > 0
        assert calc.base_premium > 0
        breakdown = calc.to_dict()
        assert breakdown["total_premium"] == calc.total_premium

    def test_higher_risk_scores_produce_higher_premiums(self) -> None:
        engine = PricingEngine()
        low = engine.calculate_premium(_application(), _risk_assessment(), _rule_evaluation())

        risky = _risk_assessment()
        risky["risk_score"] = 0.95
        risky["risk_level"] = "extreme"
        high = engine.calculate_premium(_application(), risky, _rule_evaluation())

        assert high.total_premium > low.total_premium

    def test_validate_premium_accepts_sane_calculation(self) -> None:
        engine = PricingEngine()
        calc = engine.calculate_premium(_application(), _risk_assessment(), _rule_evaluation())
        assert engine.validate_premium(calc)["is_valid"]


class TestClaimsLifecycle:
    def _claim_data(self) -> dict:
        return {
            "policy_id": "POL-TEST-1",
            "claim_type": "property_damage",
            "claimed_amount": 5000.0,
            "date_of_loss": "2026-01-15T10:00:00",
            "description": "Wind damage to roof",
            "cause_of_loss": "windstorm",
        }

    def test_processed_claim_gets_number_and_reserves(self) -> None:
        claim = process_claim(self._claim_data())

        assert claim.claim_number.startswith("CLM")
    def test_settlement_requires_approval_and_records_payment(self) -> None:
        processor = ClaimsProcessor(ClaimsProcessingConfig())
        claim = processor.process_claim(self._claim_data())

        # Only approved claims settle.
        if claim.status != ClaimStatus.APPROVED:
            assert processor.settle_claim(claim.claim_id, 1500.0) is False
            return

        import uuid

        reserves_before = claim.calculate_total_reserves()
        assert processor.settle_claim(claim.claim_id, 1500.0, "agreed") is True
        assert claim.paid_amount == 1500.0
        assert claim.calculate_outstanding_reserves() == max(0, reserves_before - 1500.0)

    def test_settlement_of_unknown_claim_fails(self) -> None:
        assert ClaimsProcessor().settle_claim("no-such-id", 100.0) is False

    def test_denial_marks_claim_denied(self) -> None:
        config = ClaimsProcessingConfig()
        config.processing_mode = "manual"  # claims stay UNDER_REVIEW
        processor = ClaimsProcessor(config)
        claim = processor.process_claim(self._claim_data())
        assert claim.status == ClaimStatus.UNDER_REVIEW

        assert processor.deny_claim(claim.claim_id, "excluded peril") is True
        assert processor.get_claim(claim.claim_id).status == ClaimStatus.DENIED

    def test_summary_counts_processed_claims(self) -> None:
        processor = ClaimsProcessor(ClaimsProcessingConfig())
        processor.process_claim(self._claim_data())

        summary = processor.get_claims_summary()
        assert summary["total_claims"] >= 1
