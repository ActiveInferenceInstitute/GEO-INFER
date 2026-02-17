"""Tests for the policy analysis engine."""

import numpy as np
import pytest
from geo_infer_econ.core.policy_engine import (
    PolicyAnalysisEngine,
    PolicyScenario,
    PolicyType,
    PolicyImpact,
)


class TestPolicyAnalysisEngine:
    """Tests for policy analysis engine."""

    def setup_method(self) -> None:
        self.engine = PolicyAnalysisEngine()
        self.engine.add_baseline_data(
            "gdp", {"region_A": 1_000_000.0, "region_B": 500_000.0}
        )
        self.engine.add_baseline_data(
            "emissions", {"region_A": 50000.0, "region_B": 30000.0}
        )

    def test_define_scenario(self) -> None:
        scenario = PolicyScenario(
            name="test_fiscal",
            description="Test fiscal policy",
            policy_type=PolicyType.FISCAL,
            parameters={"tax_rate_change": 5.0},
        )
        self.engine.define_scenario(scenario)
        assert "test_fiscal" in self.engine.scenarios

    def test_assess_fiscal_policy_gdp_impact(self) -> None:
        scenario = PolicyScenario(
            name="spending_boost",
            description="Increase spending",
            policy_type=PolicyType.FISCAL,
            parameters={
                "government_spending_change": 10.0,
                "tax_rate_change": 0.0,
                "transfer_payments_change": 0.0,
                "spending_multiplier": 1.5,
            },
        )
        impact = self.engine.assess_fiscal_policy(scenario)
        assert isinstance(impact, PolicyImpact)
        assert "region_A" in impact.gdp_impact
        assert impact.gdp_impact["region_A"] > 0

    def test_assess_fiscal_policy_wrong_type_raises(self) -> None:
        scenario = PolicyScenario(
            name="infra",
            description="Infrastructure",
            policy_type=PolicyType.INFRASTRUCTURE,
            parameters={},
        )
        with pytest.raises(ValueError, match="fiscal"):
            self.engine.assess_fiscal_policy(scenario)

    def test_assess_fiscal_policy_employment_impact(self) -> None:
        scenario = PolicyScenario(
            name="tax_cut",
            description="Tax reduction",
            policy_type=PolicyType.FISCAL,
            parameters={
                "tax_rate_change": -5.0,
                "government_spending_change": 0.0,
                "transfer_payments_change": 0.0,
            },
        )
        impact = self.engine.assess_fiscal_policy(scenario)
        assert "region_A" in impact.employment_impact

    def test_assess_infrastructure_policy(self) -> None:
        scenario = PolicyScenario(
            name="roads",
            description="Road investment",
            policy_type=PolicyType.INFRASTRUCTURE,
            parameters={
                "investment_amount": 100_000.0,
                "type": "transport",
                "regional_allocation": {"region_A": 0.6, "region_B": 0.4},
                "cost_per_job": 50_000.0,
                "permanent_job_ratio": 0.1,
                "accessibility_improvement": 0.05,
            },
        )
        impact = self.engine.assess_infrastructure_policy(scenario)
        assert impact.scenario_name == "roads"
        assert impact.spatial_spillovers is not None

    def test_assess_environmental_policy(self) -> None:
        scenario = PolicyScenario(
            name="carbon_tax",
            description="Carbon pricing",
            policy_type=PolicyType.ENVIRONMENTAL,
            parameters={
                "carbon_tax": 25.0,
                "green_subsidies": 50_000.0,
                "carbon_intensity": 0.5,
            },
        )
        impact = self.engine.assess_environmental_policy(scenario)
        assert "region_A" in impact.welfare_impact

    def test_compare_scenarios(self) -> None:
        s1 = PolicyScenario(
            name="scenario_A",
            description="Fiscal option A",
            policy_type=PolicyType.FISCAL,
            parameters={
                "government_spending_change": 10.0,
                "tax_rate_change": 0.0,
                "transfer_payments_change": 0.0,
            },
        )
        s2 = PolicyScenario(
            name="scenario_B",
            description="Fiscal option B",
            policy_type=PolicyType.FISCAL,
            parameters={
                "government_spending_change": 5.0,
                "tax_rate_change": -2.0,
                "transfer_payments_change": 3.0,
            },
        )
        self.engine.define_scenario(s1)
        self.engine.define_scenario(s2)
        comparison = self.engine.compare_scenarios(["scenario_A", "scenario_B"])
        assert len(comparison.ranking) == 2
        assert len(comparison.recommendations) > 0

    def test_compare_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="At least one"):
            self.engine.compare_scenarios([])

    def test_no_baseline_gdp_raises(self) -> None:
        engine = PolicyAnalysisEngine()
        scenario = PolicyScenario(
            name="no_data",
            description="No baseline",
            policy_type=PolicyType.FISCAL,
            parameters={"government_spending_change": 5.0},
        )
        with pytest.raises(ValueError, match="Baseline GDP"):
            engine.assess_fiscal_policy(scenario)
