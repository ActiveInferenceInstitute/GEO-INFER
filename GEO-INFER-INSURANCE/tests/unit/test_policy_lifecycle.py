"""Behavioral tests for the policy lifecycle (GS-146).

Covers PolicyManager bind/activate/renew/cancel transitions, guard rails
against invalid transitions, renewal economics, cancellation refunds, and
endorsement handling.
"""

from datetime import datetime, timedelta

from geo_infer_insurance.underwriting.core.policy_management import (
    CoverageType,
    Endorsement,
    Policy,
    PolicyManager,
    PolicyStatus,
)


def _application(**overrides) -> dict:
    data = {
        "policyholder_id": "ph-001",
        "property_id": "prop-001",
        "effective_date": datetime.now() - timedelta(days=1),
        "term_months": 12,
        "coverage_requests": [
            {"coverage_type": "property", "limit": 500000, "deductible": 5000},
            {"coverage_type": "flood", "limit": 100000},
        ],
    }
    data.update(overrides)
    return data


def _premium() -> dict:
    return {
        "total_premium": 2400.0,
        "base_premium": 2000.0,
        "coverage_breakdown": {"property": 1800.0, "flood": 600.0},
    }


def _decision(risk_score: float = 0.4) -> dict:
    return {"risk_score": risk_score}


def _manager() -> PolicyManager:
    return PolicyManager()


class TestPolicyCreation:
    def test_create_policy_starts_quoted_with_coverages(self) -> None:
        manager = _manager()

        policy = manager.create_policy(_application(), _premium(), _decision())

        assert policy.status == PolicyStatus.QUOTED
        assert policy.policy_number.startswith("POL")
        assert policy.total_premium == 2400.0
        assert {c.coverage_type for c in policy.coverages} == {
            CoverageType.PROPERTY,
            CoverageType.FLOOD,
        }
        assert manager.get_policy(policy.policy_id) is policy

    def test_risk_tier_maps_risk_score_bands(self) -> None:
        manager = _manager()

        preferred = manager.create_policy(_application(), _premium(), _decision(0.1))
        standard = manager.create_policy(_application(), _premium(), _decision(0.4))
        high = manager.create_policy(_application(), _premium(), _decision(0.7))
        decline = manager.create_policy(_application(), _premium(), _decision(0.9))

        assert preferred.risk_tier == "preferred"
        assert standard.risk_tier == "standard"
        assert high.risk_tier == "high"
        assert decline.risk_tier == "decline"

    def test_expiration_derived_from_term(self) -> None:
        manager = _manager()
        effective = datetime.now() - timedelta(days=1)

        policy = manager.create_policy(
            _application(effective_date=effective), _premium(), _decision()
        )

        assert policy.expiration_date - policy.effective_date == timedelta(days=360)


class TestLifecycleTransitions:
    def test_full_lifecycle_bind_activate_renew(self) -> None:
        manager = _manager()
        policy = manager.create_policy(_application(), _premium(), _decision())

        assert manager.bind_policy(policy.policy_id) is True
        assert policy.status == PolicyStatus.BOUND

        assert manager.activate_policy(policy.policy_id) is True
        assert policy.status == PolicyStatus.ACTIVE

        renewal = manager.renew_policy(policy.policy_id)
        assert renewal is not None
        assert policy.status == PolicyStatus.RENEWED
        assert renewal.status == PolicyStatus.QUOTED
        assert renewal.policy_id != policy.policy_id
        assert policy.metadata["renewed_to"] == renewal.policy_id

    def test_renewal_starts_day_after_original_expiration_with_discount(self) -> None:
        manager = _manager()
        policy = manager.create_policy(_application(), _premium(), _decision())
        manager.bind_policy(policy.policy_id)
        manager.activate_policy(policy.policy_id)

        renewal = manager.renew_policy(policy.policy_id, renewal_term_months=6)

        assert renewal.effective_date == policy.expiration_date + timedelta(days=1)
        assert renewal.expiration_date == policy.expiration_date + timedelta(days=180)
        assert renewal.total_premium == policy.total_premium * 0.95

    def test_bind_requires_quoted_status(self) -> None:
        manager = _manager()
        policy = manager.create_policy(_application(), _premium(), _decision())
        manager.bind_policy(policy.policy_id)

        assert manager.bind_policy(policy.policy_id) is False
        assert policy.status == PolicyStatus.BOUND

    def test_activate_requires_bound_status(self) -> None:
        manager = _manager()
        policy = manager.create_policy(_application(), _premium(), _decision())

        assert manager.activate_policy(policy.policy_id) is False
        assert policy.status == PolicyStatus.QUOTED

    def test_renew_requires_active_status(self) -> None:
        manager = _manager()
        policy = manager.create_policy(_application(), _premium(), _decision())
        manager.bind_policy(policy.policy_id)

        assert manager.renew_policy(policy.policy_id) is None
        assert policy.status == PolicyStatus.BOUND

    def test_cancel_active_policy_records_refund(self) -> None:
        manager = _manager()
        policy = manager.create_policy(_application(), _premium(), _decision())
        manager.bind_policy(policy.policy_id)
        manager.activate_policy(policy.policy_id)

        assert manager.cancel_policy(policy.policy_id, reason="insured request") is True
        assert policy.status == PolicyStatus.CANCELLED
        refund = policy.metadata["cancellation_refund"]
        assert refund > 0
        assert refund < policy.total_premium

    def test_cancel_unknown_policy_fails(self) -> None:
        manager = _manager()

        assert manager.cancel_policy("nonexistent", reason="test") is False

    def test_operations_on_unknown_policy_ids_fail(self) -> None:
        manager = _manager()

        assert manager.bind_policy("nonexistent") is False
        assert manager.activate_policy("nonexistent") is False
        assert manager.renew_policy("nonexistent") is None
        assert manager.get_policy("nonexistent") is None

    def test_policy_without_coverages_cannot_bind(self) -> None:
        manager = _manager()
        policy = Policy(
            policy_id="bare-policy",
            policy_number="POLBARE",
            status=PolicyStatus.QUOTED,
            policyholder_id="ph-x",
            property_id="prop-x",
            effective_date=datetime.now(),
            expiration_date=datetime.now() + timedelta(days=30),
        )
        manager.policies[policy.policy_id] = policy

        assert manager.bind_policy(policy.policy_id) is False
        assert policy.status == PolicyStatus.QUOTED


class TestEndorsementsAndSearch:
    def _bound_policy(self, manager: PolicyManager):
        policy = manager.create_policy(_application(), _premium(), _decision())
        assert manager.bind_policy(policy.policy_id) is True
        return policy

    def test_add_endorsement_applies_premium_change(self) -> None:
        manager = _manager()
        policy = self._bound_policy(manager)
        endorsement = Endorsement(
            endorsement_id="end-001",
            endorsement_type="coverage_increase",
            effective_date=datetime.now(),
            description="raise property limit",
            premium_change=150.0,
        )

        assert manager.add_endorsement(policy.policy_id, endorsement) is True
        assert policy.total_premium == 2400.0 + 150.0

    def test_add_endorsement_unknown_policy_fails(self) -> None:
        manager = _manager()

        assert (
            manager.add_endorsement(
                "nonexistent",
                Endorsement(
                    endorsement_id="end-x",
                    endorsement_type="misc",
                    effective_date=datetime.now(),
                    description="n/a",
                ),
            )
            is False
        )

    def test_search_policies_filters_by_status_and_policyholder(self) -> None:
        manager = _manager()
        bound = manager.create_policy(_application(), _premium(), _decision())
        manager.bind_policy(bound.policy_id)
        other = manager.create_policy(
            _application(policyholder_id="ph-002"), _premium(), _decision()
        )

        bound_matches = manager.search_policies({"status": PolicyStatus.BOUND})
        holder_matches = manager.search_policies({"policyholder_id": "ph-002"})

        assert [p.policy_id for p in bound_matches] == [bound.policy_id]
        assert [p.policy_id for p in holder_matches] == [other.policy_id]

    def test_update_policy_changes_fields(self) -> None:
        manager = _manager()
        policy = manager.create_policy(_application(), _premium(), _decision())

        assert manager.update_policy(policy.policy_id, {"risk_score": 0.9}) is True
        assert policy.risk_score == 0.9
        assert manager.update_policy("nonexistent", {"risk_score": 0.9}) is False
