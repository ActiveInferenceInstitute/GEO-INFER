"""Tests for policy impact assessment: cost-benefit, stakeholder, and equity analysis."""

import math

import pytest
from geo_infer_civ.core.policy_analysis import (
    CostBenefitAnalyzer,
    CostBenefitItem,
    StakeholderImpactAnalyzer,
    StakeholderImpact,
    ImpactLevel,
    EquityAnalyzer,
)


@pytest.fixture
def cba():
    return CostBenefitAnalyzer(discount_rate=0.05)


@pytest.fixture
def stakeholder_analyzer():
    return StakeholderImpactAnalyzer()


@pytest.fixture
def equity_analyzer():
    return EquityAnalyzer()


class TestCostBenefitAnalyzer:
    def test_empty_raises(self, cba):
        with pytest.raises(ValueError, match="No cost-benefit"):
            cba.analyze()

    def test_simple_analysis(self, cba):
        cba.add_item(CostBenefitItem("construction", 1_000_000, is_benefit=False, time_horizon_years=0))
        cba.add_item(CostBenefitItem("revenue", 500_000, is_benefit=True, time_horizon_years=1))
        cba.add_item(CostBenefitItem("revenue", 500_000, is_benefit=True, time_horizon_years=2))
        cba.add_item(CostBenefitItem("revenue", 500_000, is_benefit=True, time_horizon_years=3))
        result = cba.analyze()
        assert result.total_costs > 0
        assert result.total_benefits > 0
        assert result.benefit_cost_ratio > 1.0
        assert result.net_present_value > 0

    def test_negative_npv(self, cba):
        cba.add_item(CostBenefitItem("cost", 1_000_000, is_benefit=False))
        cba.add_item(CostBenefitItem("benefit", 100_000, is_benefit=True, time_horizon_years=1))
        result = cba.analyze()
        assert result.net_present_value < 0
        assert result.benefit_cost_ratio < 1.0

    def test_risk_adjusted(self, cba):
        cba.add_item(CostBenefitItem("cost", 100_000, is_benefit=False, probability=1.0))
        cba.add_item(CostBenefitItem("benefit_certain", 80_000, is_benefit=True, probability=1.0))
        cba.add_item(CostBenefitItem("benefit_risky", 80_000, is_benefit=True, probability=0.5))
        result = cba.analyze()
        assert result.risk_adjusted_npv < result.net_present_value

    def test_category_breakdown(self, cba):
        cba.add_item(CostBenefitItem("road", 500_000, is_benefit=False, category="infrastructure"))
        cba.add_item(CostBenefitItem("toll", 200_000, is_benefit=True, category="revenue"))
        result = cba.analyze()
        assert "infrastructure" in result.category_breakdown
        assert "revenue" in result.category_breakdown

    def test_invalid_discount_rate(self):
        with pytest.raises(ValueError):
            CostBenefitAnalyzer(discount_rate=1.5)

    def test_payback_period(self, cba):
        cba.add_item(CostBenefitItem("cost", 1000, is_benefit=False, time_horizon_years=0))
        cba.add_item(CostBenefitItem("income", 400, is_benefit=True, time_horizon_years=1))
        cba.add_item(CostBenefitItem("income", 400, is_benefit=True, time_horizon_years=2))
        cba.add_item(CostBenefitItem("income", 400, is_benefit=True, time_horizon_years=3))
        result = cba.analyze()
        assert result.payback_period_years > 0
        assert result.payback_period_years <= 4

    def test_payback_period_inf_when_never_recovered(self, cba):
        """A proposal that never breaks even reports an infinite payback."""
        cba.add_item(CostBenefitItem("cost", 1000, is_benefit=False, time_horizon_years=0))
        cba.add_item(CostBenefitItem("income", 100, is_benefit=True, time_horizon_years=1))
        result = cba.analyze()
        assert result.payback_period_years == float("inf")

    def test_irr_is_nan_without_sign_crossing(self, cba):
        """Pure-cost or pure-benefit item sets have no IRR; result is nan."""
        cba.add_item(CostBenefitItem("cost", 1000, is_benefit=False, time_horizon_years=0))
        cba.add_item(CostBenefitItem("cost", 500, is_benefit=False, time_horizon_years=1))
        result = cba.analyze()
        assert math.isnan(result.internal_rate_of_return)

    def test_irr_lands_between_bisection_bounds(self, cba):
        """A net-positive proposal yields a finite IRR in the searched range."""
        cba.add_item(CostBenefitItem("cost", 1000, is_benefit=False, time_horizon_years=0))
        cba.add_item(CostBenefitItem("income", 600, is_benefit=True, time_horizon_years=1))
        result = cba.analyze()
        assert -0.5 < result.internal_rate_of_return < 2.0


class TestStakeholderImpactAnalyzer:
    def test_empty_raises(self, stakeholder_analyzer):
        with pytest.raises(ValueError, match="No stakeholder"):
            stakeholder_analyzer.compute_impact_matrix()

    def test_impact_matrix(self, stakeholder_analyzer):
        stakeholder_analyzer.add_impact(StakeholderImpact(
            "residents", 10000, ImpactLevel.POSITIVE,
            economic_impact=0.5, quality_of_life_impact=0.8,
            environmental_impact=0.3, accessibility_impact=0.6,
        ))
        stakeholder_analyzer.add_impact(StakeholderImpact(
            "businesses", 500, ImpactLevel.VERY_POSITIVE,
            economic_impact=1.0, quality_of_life_impact=0.2,
            environmental_impact=-0.3, accessibility_impact=0.5,
        ))
        matrix = stakeholder_analyzer.compute_impact_matrix()
        assert "residents" in matrix
        assert "businesses" in matrix
        assert "weighted_composite" in matrix["residents"]
        assert -1.0 <= matrix["residents"]["weighted_composite"] <= 1.0

    def test_aggregate_score(self, stakeholder_analyzer):
        stakeholder_analyzer.add_impact(StakeholderImpact(
            "group_a", 1000, ImpactLevel.POSITIVE,
            economic_impact=0.5, quality_of_life_impact=0.5,
        ))
        stakeholder_analyzer.add_impact(StakeholderImpact(
            "group_b", 1000, ImpactLevel.NEGATIVE,
            economic_impact=-0.5, quality_of_life_impact=-0.5,
        ))
        score = stakeholder_analyzer.compute_aggregate_score()
        # Roughly neutral since groups are equal sized with opposite impacts
        assert abs(score) < 0.5

    def test_most_affected(self, stakeholder_analyzer):
        stakeholder_analyzer.add_impact(StakeholderImpact(
            "winners", 500, ImpactLevel.VERY_POSITIVE,
            economic_impact=2.0, quality_of_life_impact=2.0,
            environmental_impact=1.0, accessibility_impact=1.0,
        ))
        stakeholder_analyzer.add_impact(StakeholderImpact(
            "losers", 500, ImpactLevel.VERY_NEGATIVE,
            economic_impact=-2.0, quality_of_life_impact=-2.0,
            environmental_impact=-1.0, accessibility_impact=-1.0,
        ))
        best, worst = stakeholder_analyzer.find_most_affected()
        assert best == "winners"
        assert worst == "losers"


class TestEquityAnalyzer:
    def test_fewer_than_two_groups_raises(self, equity_analyzer):
        equity_analyzer.set_group_impact("only_group", 1.0, 100)
        with pytest.raises(ValueError, match="At least 2"):
            equity_analyzer.analyze()

    def test_perfect_equity(self, equity_analyzer):
        equity_analyzer.set_group_impact("group_a", 1.0, 100)
        equity_analyzer.set_group_impact("group_b", 1.0, 100)
        equity_analyzer.set_group_impact("group_c", 1.0, 100)
        result = equity_analyzer.analyze()
        assert result.gini_coefficient == 0.0
        assert result.overall_equity_score == 1.0
        assert len(result.disparate_impact_flags) == 0

    def test_high_inequality(self, equity_analyzer):
        equity_analyzer.set_group_impact("wealthy", 10.0, 100)
        equity_analyzer.set_group_impact("poor", 0.1, 900)
        result = equity_analyzer.analyze()
        assert result.gini_coefficient > 0.0
        assert result.overall_equity_score < 1.0
        assert len(result.disparate_impact_flags) > 0

    def test_disparate_impact_flags(self, equity_analyzer):
        equity_analyzer.set_group_impact("favored", 100.0, 500)
        equity_analyzer.set_group_impact("neutral", 50.0, 500)
        equity_analyzer.set_group_impact("disfavored", 10.0, 500)
        result = equity_analyzer.analyze()
        assert any("disfavored" in f for f in result.disparate_impact_flags)

    def test_most_and_least_impacted(self, equity_analyzer):
        equity_analyzer.set_group_impact("high", 5.0, 100)
        equity_analyzer.set_group_impact("low", 1.0, 100)
        result = equity_analyzer.analyze()
        assert result.most_impacted_group == "high"
        assert result.least_impacted_group == "low"
