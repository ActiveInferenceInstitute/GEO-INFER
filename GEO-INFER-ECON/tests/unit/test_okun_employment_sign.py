"""Regression tests for Okun's-law employment-impact sign in fiscal assessment."""

import pytest
from geo_infer_econ.core.policy_engine import (
    PolicyAnalysisEngine,
    PolicyScenario,
    PolicyType,
)


class TestOkunEmploymentSign:
    """Okun's law: employment must move in the same direction as GDP impact."""

    def setup_method(self) -> None:
        self.engine = PolicyAnalysisEngine()
        self.engine.add_baseline_data("gdp", {"r": 1_000_000.0})

    def _fiscal_scenario(self, parameters: dict) -> PolicyScenario:
        return PolicyScenario(
            name="okun_probe",
            description="Okun sign regression probe",
            policy_type=PolicyType.FISCAL,
            parameters=parameters,
        )

    def test_expansionary_spending_yields_positive_employment_impact(self) -> None:
        scenario = self._fiscal_scenario({"government_spending_change": 10.0})
        impact = self.engine.assess_fiscal_policy(scenario)
        # +10 spending shock, default spending_multiplier 1.5 -> +15pp GDP
        # shock; Okun's law must map that to a positive employment impact.
        assert impact.gdp_impact["r"] > 0
        assert impact.employment_impact["r"] > 0

    def test_employment_impact_matches_okun_magnitude(self) -> None:
        scenario = self._fiscal_scenario({"government_spending_change": 10.0})
        impact = self.engine.assess_fiscal_policy(scenario)
        # gdp_change = 10 * 1.5 = 15; default |okun_coefficient| = 2.0
        assert impact.employment_impact["r"] == pytest.approx(15.0 / 2.0)

    def test_contractionary_shock_yields_negative_employment_impact(self) -> None:
        scenario = self._fiscal_scenario({"government_spending_change": -10.0})
        impact = self.engine.assess_fiscal_policy(scenario)
        assert impact.gdp_impact["r"] < 0
        assert impact.employment_impact["r"] < 0

    def test_positive_okun_coefficient_convention_also_yields_correct_sign(
        self,
    ) -> None:
        scenario = self._fiscal_scenario(
            {"government_spending_change": 10.0, "okun_coefficient": 2.0}
        )
        impact = self.engine.assess_fiscal_policy(scenario)
        assert impact.employment_impact["r"] > 0

    def test_zero_okun_coefficient_raises_value_error(self) -> None:
        scenario = self._fiscal_scenario(
            {"government_spending_change": 10.0, "okun_coefficient": 0}
        )
        with pytest.raises(ValueError, match="okun_coefficient"):
            self.engine.assess_fiscal_policy(scenario)
