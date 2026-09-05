"""
Integration tests for GEO-INFER-INSURANCE.

Exercises the real end-to-end underwriting lifecycle through the package's
public API only: create an underwriting system, underwrite a policy
application to a decision, and process a claim against the resulting
policy. No mocks — every step runs the module's own engines.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

import geo_infer_insurance
from geo_infer_insurance import UnderwritingConfig, create_underwriting_system


@pytest.mark.integration
class TestInsuranceIntegration:
    """Test insurance module integration through the public API."""

    def test_module_integration(self) -> None:
        """The package imports and its public surface is intact."""
        for name in geo_infer_insurance.__all__:
            assert hasattr(geo_infer_insurance, name), name
            assert getattr(geo_infer_insurance, name) is not None, name

    def _application(self) -> dict:
        """A well-formed residential application for a low-risk property."""
        return {
            "property": {
                "type": "residential",
                "value": 450000,
                "year_built": 2010,
                "construction": "frame",
                "territory": "urban",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
            "applicant": {
                "name": "Jane Doe",
                "contact_info": {"email": "jane.doe@example.com"},
            },
            "coverage_requests": [
                {
                    "coverage_type": "property",
                    "limit": 450000,
                    "deductible": 5000,
                },
            ],
        }

    def test_end_to_end_underwrite_policy_and_claim(self) -> None:
        """System creation -> underwriting decision -> policy -> claim."""
        # Auto-decisions at a combined score >= 0.7 so a clean low-risk
        # application binds without human referral.
        config = UnderwritingConfig(auto_decision_threshold=0.7)
        system = create_underwriting_system(config)

        # Step 1: underwrite the application to a final decision.
        case = system.underwrite_policy(self._application())

        assert case.completed_at is not None
        assert case.error_message is None
        assert case.status == "approved"
        assert case.decision is not None
        decision = case.decision
        assert decision.approved is True
        assert 0.0 <= decision.confidence <= 1.0
        assert decision.risk_score is not None
        assert decision.rule_score is not None
        assert case.premium is not None and case.premium > 0

        # Step 2: an approved decision must have produced a bound policy.
        assert case.policy is not None
        policy = case.policy
        assert policy["policy_id"]
        assert policy["policy_number"]
        assert policy["total_premium"] > 0
        assert len(policy["coverages"]) == 1
        assert policy["coverages"][0]["limit"] == 450000

        # The policy is registered in the portfolio.
        summary = system.get_portfolio_summary()
        assert summary["total_premium"] > 0

        # Step 3: file a claim against the underwritten policy.
        claim_data = {
            "policy_id": policy["policy_id"],
            "claim_type": "property_damage",
            "claimed_amount": 5000.0,
            "date_of_loss": datetime.now().isoformat(),
            "reported_date": (datetime.now() + timedelta(hours=2)).isoformat(),
            "description": "Wind damage to roof shingles during storm",
            "cause_of_loss": "windstorm",
        }
        claim = system.process_claim(claim_data)

        assert claim.claim_id not in ("INVALID", "ERROR")
        assert claim.claim_number.startswith("CLM")
        assert claim.policy_id == policy["policy_id"]
        assert claim.claimed_amount == pytest.approx(5000.0)
        assert claim.calculate_total_reserves() > 0
        assert claim.calculate_outstanding_reserves() > 0
        assert not claim.is_closed()

        # The case retains the full audit artifacts of the decision.
        status = system.get_case_status(case.case_id)
        assert status is not None
