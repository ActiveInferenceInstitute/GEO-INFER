"""Regression tests for the in-memory underwriting portfolio boundary."""

from geo_infer_insurance.underwriting import create_pricing_engine
from geo_infer_insurance.underwriting.core.portfolio_management import (
    PortfolioManager,
    PortfolioOptimizer,
)


def test_portfolio_manager_aggregates_policy_and_claim_metrics() -> None:
    manager = PortfolioManager()
    manager.add_policy(
        {
            "policy_id": "policy-1",
            "status": "active",
            "premium": 1000,
            "limit": 100000,
            "risk_score": 0.25,
            "region": "west",
        },
        portfolio_id="regional",
    )
    manager.update_portfolio_metrics(
        {"claim_id": "claim-1", "policy_id": "policy-1", "amount": 250}
    )

    summary = manager.get_portfolio_summary("regional")

    assert summary["total_policies"] == 1
    assert summary["active_policies"] == 1
    assert summary["total_exposure"] == 100000.0
    assert summary["total_claims"] == 250.0
    assert summary["loss_ratio"] == 0.25
    assert summary["exposure_by_region"] == {"west": 100000.0}


def test_portfolio_optimizer_flags_capacity_breach() -> None:
    result = PortfolioOptimizer().optimize(
        [{"policy_id": "policy-1", "premium": 100, "limit": 1000}],
        max_exposure=500,
    )

    assert result["capacity_exceeded"] is True
    assert result["recommended_order"][0]["policy_id"] == "policy-1"
    # The convenience factory must return a working pricing engine, not just
    # any object: a minimal application must price with a positive premium.
    from geo_infer_insurance.underwriting.core.pricing_engine import PricingEngine

    engine = create_pricing_engine()
    assert isinstance(engine, PricingEngine)
    application = {
        "property": {"type": "residential", "value": 200000, "year_built": 2010},
        "coverage_requests": [{"coverage_type": "dwelling", "limit": 200000}],
    }
    risk_assessment = {"risk_score": 0.3, "risk_level": "moderate", "factors": {}}
    rule_evaluation = {"passed": True, "violations": [], "adjustments": []}
    assert (
        engine.calculate_premium(
            application, risk_assessment, rule_evaluation
        ).total_premium
        > 0
    )
