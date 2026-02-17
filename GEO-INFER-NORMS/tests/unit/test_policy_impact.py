"""Tests for the policy impact analysis module."""
import pytest
import pandas as pd
import geopandas as gpd
from types import SimpleNamespace

from geo_infer_norms.core.policy_impact import (
    PolicyImpactAnalyzer,
    RegulatoryImpactAssessment,
)


def _make_policy(policy_type: str = "zoning_change", **attrs):
    ns = SimpleNamespace(policy_type=policy_type, **attrs)
    return ns


class TestPolicyImpactAnalyzer:
    def test_init(self):
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy(),
            context_data={},
        )
        assert analyzer.policy is not None

    def test_analyze_economic_impact_no_data(self):
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy(),
            context_data={},
        )
        result = analyzer.analyze_economic_impact()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert "impact_category" in result.columns

    def test_analyze_economic_impact_with_data(self):
        context = {
            "economic_data": {
                "property_values": {"total_value": 1_000_000},
                "business_activity": {"revenue": 500_000},
                "employment": {"total_jobs": 100},
                "tax_revenue": {"annual_revenue": 200_000},
            }
        }
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy("zoning_change", zoning_details={"upzoning": True}),
            context_data=context,
        )
        result = analyzer.analyze_economic_impact()
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 4

    def test_analyze_social_equity_impact_no_data(self):
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy(),
            context_data={},
        )
        result = analyzer.analyze_social_equity_impact()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_analyze_social_equity_impact_with_demographics(self):
        context = {
            "demographic_data": {
                "access_metrics": {
                    "groups": [
                        {"name": "A", "access_score": 0.9},
                        {"name": "B", "access_score": 0.4},
                    ]
                },
                "housing": {"avg_rent_burden": 0.35},
                "income_distribution": {"gini_coefficient": 0.42},
            }
        }
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy("economic_development"),
            context_data=context,
        )
        result = analyzer.analyze_social_equity_impact()
        assert isinstance(result, pd.DataFrame)
        assert "equity_dimension" in result.columns
        assert len(result) == 3

    def test_analyze_environmental_impact_no_data(self):
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy(),
            context_data={},
        )
        result = analyzer.analyze_environmental_impact()
        assert isinstance(result, (pd.DataFrame, gpd.GeoDataFrame))
        assert len(result) == 3

    def test_analyze_environmental_impact_with_data(self):
        context = {
            "environmental_data": {
                "land_cover": {"projected_change_pct": 3.0},
                "air_quality": {"baseline_aqi": 45},
                "water_quality": {"baseline_wqi": 72},
            }
        }
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy("environmental"),
            context_data=context,
        )
        result = analyzer.analyze_environmental_impact()
        assert len(result) == 3

    def test_generate_impact_report(self):
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy(),
            context_data={},
        )
        report = analyzer.generate_impact_report()
        assert "economic" in report
        assert "social_equity" in report
        assert "environmental" in report
        assert "summary" in report

    def test_visualize_spatial_impact_no_extent(self):
        analyzer = PolicyImpactAnalyzer(
            policy=_make_policy(),
            context_data={},
            spatial_extent=None,
        )
        result = analyzer.visualize_spatial_impact()
        assert result is None


class TestRegulatoryImpactAssessment:
    def _make_entities(self, count: int = 5):
        return gpd.GeoDataFrame({
            "entity_id": [f"e-{i}" for i in range(count)],
            "category": ["industrial"] * 3 + ["commercial"] * (count - 3),
        })

    def test_estimate_compliance_costs(self):
        ria = RegulatoryImpactAssessment(
            regulation="Test Regulation",
            affected_entities=self._make_entities(),
            baseline_data={"compliance_costs": {"base_cost_per_entity": 2000.0, "complexity_multiplier": 1.5}},
        )
        result = ria.estimate_compliance_costs()
        assert isinstance(result, pd.DataFrame)
        assert "estimated_cost" in result.columns
        assert result["estimated_cost"].sum() > 0

    def test_assess_administrative_burden(self):
        ria = RegulatoryImpactAssessment(
            regulation="Test Regulation",
            affected_entities=self._make_entities(10),
            baseline_data={},
        )
        result = ria.assess_administrative_burden()
        assert "total_hours" in result
        assert "total_cost" in result
        assert result["entity_count"] == 10

    def test_analyze_market_effects_no_data(self):
        ria = RegulatoryImpactAssessment(
            regulation="Test Regulation",
            affected_entities=self._make_entities(),
            baseline_data={},
        )
        result = ria.analyze_market_effects()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4

    def test_analyze_market_effects_with_data(self):
        ria = RegulatoryImpactAssessment(
            regulation="Test Regulation",
            affected_entities=self._make_entities(),
            baseline_data={"market": {"market_size": 5_000_000, "num_competitors": 20, "barrier_increase_pct": 8.0, "innovation_effect": 0.1, "price_change_pct": 2.0, "projected_exit_rate": 0.03}},
        )
        result = ria.analyze_market_effects()
        assert result["market_dimension"].tolist() == ["competition", "innovation", "prices", "entry_exit"]

    def test_evaluate_goal_achievement(self):
        ria = RegulatoryImpactAssessment(
            regulation="Test Regulation",
            affected_entities=self._make_entities(),
            baseline_data={
                "regulation_goals": [
                    {"name": "reduce_emissions", "target_value": 50, "current_value": 45, "metric_type": "ratio"},
                    {"name": "increase_safety", "target_value": 1.0, "current_value": 1.0, "metric_type": "boolean"},
                ]
            },
        )
        result = ria.evaluate_goal_achievement()
        assert result["goals_evaluated"] == 2
        assert result["overall_achievement"] > 0

    def test_generate_assessment_summary(self):
        ria = RegulatoryImpactAssessment(
            regulation="Clean Air Act",
            affected_entities=self._make_entities(3),
            baseline_data={},
        )
        summary = ria.generate_assessment_summary()
        assert "Clean Air Act" in summary
        assert "Affected entities" in summary
