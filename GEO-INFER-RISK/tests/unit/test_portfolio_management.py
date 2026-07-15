"""Regression tests for the in-memory underwriting portfolio boundary."""

from geo_infer_risk.underwriting import create_pricing_engine
from geo_infer_risk.underwriting.core.portfolio_management import (
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
    assert create_pricing_engine() is not None
