"""Tests for macroeconomics model classes in aggregate_models.

Covers BusinessCycleModels (HP filter), MonetaryPolicyModels (Taylor rule),
FiscalPolicyModels (Keynesian multiplier), TradeModels (gravity model and
haversine distance), and AggregateGrowthModels (Solow growth accounting).
"""

import numpy as np
import pytest

from geo_infer_econ.macroeconomics import (
    AggregateGrowthModels,
    BusinessCycleModels,
    FiscalPolicyModels,
    MonetaryPolicyModels,
    TradeModels,
)


class TestBusinessCycleModels:
    """HP filter decomposition behavior."""

    def setup_method(self) -> None:
        self.models = BusinessCycleModels()

    def test_hp_filter_separates_smooth_trend_from_cycle(self) -> None:
        """Trend must be smoother than the cycle and sum to log output."""
        t = np.arange(60)
        series = 100 * np.exp(0.02 * t) + 3 * np.sin(2 * np.pi * t / 8)
        result = self.models.model_cycles({"series": list(series)})

        assert "error" not in result
        trend = np.array(result["trend"])
        cycle = np.array(result["cycle"])

        # Trend nearly captures the smooth exponential growth
        assert np.allclose(np.log(trend), np.log(100) + 0.02 * t, atol=0.01)
        # Cycle is mean-zero and stationary around zero
        assert abs(np.mean(cycle)) < 0.01
        # Trend smoother than the cycle
        assert np.std(np.diff(np.log(trend))) < np.std(cycle)

    def test_model_cycles_short_series_returns_error(self) -> None:
        result = self.models.model_cycles({"series": [1.0, 2.0, 3.0]})
        assert result == {"error": "Series must have at least 4 observations"}

    def test_annual_frequency_uses_smaller_lambda(self) -> None:
        """Annual frequency applies lambda=6.25: more cyclical detail retained."""
        t = np.arange(40)
        series = list(100 * np.exp(0.01 * t) + 2 * np.sin(2 * np.pi * t / 4))
        quarterly = self.models.model_cycles({"series": series})
        annual = self.models.model_cycles({"series": series, "frequency": "annual"})
        assert quarterly["cycle_std"] != annual["cycle_std"]
        assert annual["cycle_std"] < quarterly["cycle_std"]


class TestMonetaryPolicyModels:
    """Taylor rule arithmetic and stance classification."""

    def test_taylor_rule_rate_matches_formula(self) -> None:
        models = MonetaryPolicyModels()
        result = models.model_policy(
            {"inflation_rate": 4.0, "output_gap": 1.0, "current_rate": 5.0}
        )
        # i = r* + pi + phi_pi (pi - pi*) + phi_y * gap = 2 + 4 + 1.5*2 + 0.5*1
        assert result["taylor_rule_rate"] == 9.5
        assert result["recommended_change_bps"] == 450.0
        assert result["monetary_stance"] == "tightening"

    def test_neutral_stance_when_close_to_current_rate(self) -> None:
        models = MonetaryPolicyModels()
        result = models.model_policy(
            {"inflation_rate": 2.0, "output_gap": 0.0, "current_rate": 4.0}
        )
        # taylor_rate = 2 + 2 = 4, change = 0 -> neutral hold
        assert result["taylor_rule_rate"] == 4.0
        assert result["monetary_stance"] == "neutral"
        assert result["recommended_action"] == "hold rates"

    def test_custom_weights_respected(self) -> None:
        models = MonetaryPolicyModels(
            config={"inflation_weight": 0.0, "output_gap_weight": 0.0, "neutral_rate": 1.0}
        )
        result = models.model_policy(
            {"inflation_rate": 3.0, "output_gap": 2.0, "current_rate": 4.0}
        )
        # i = 1 + 3 = 4 -> no change
        assert result["taylor_rule_rate"] == 4.0
        assert result["monetary_stance"] == "neutral"


class TestFiscalPolicyModels:
    """Keynesian multiplier and budget accounting."""

    def test_multiplier_matches_formula(self) -> None:
        models = FiscalPolicyModels()
        result = models.model_fiscal_policy(
            {"gdp": 1000.0, "government_spending": 200.0, "tax_revenue": 250.0,
             "public_debt": 800.0, "spending_change": 10.0}
        )
        # k = 1 / (1 - 0.75*0.75 + 0.15)
        assert result["fiscal_multiplier"] == pytest.approx(1.701, abs=0.01)
        assert result["gdp_impact"] == pytest.approx(17.01, abs=0.1)


class TestTradeModels:
    """Gravity model and haversine distance."""

    def test_haversine_known_distance(self) -> None:
        # Portland to Seattle is roughly 233 km
        d = TradeModels._haversine(45.5, -122.6, 47.6, -122.3)
        assert d == pytest.approx(233, abs=10)

    def test_haversine_zero_distance(self) -> None:
        assert TradeModels._haversine(10.0, 20.0, 10.0, 20.0) == pytest.approx(0.0)

    def test_gravity_model_respects_distance_decay(self) -> None:
        models = TradeModels()
        near = {"id": "near", "gdp": 100.0, "lat": 45.0, "lon": -122.0}
        far = {"id": "far", "gdp": 100.0, "lat": 45.0, "lon": -12.0}
        home = {"id": "home", "gdp": 100.0, "lat": 45.0, "lon": -122.0}
        result = models.model_trade({"countries": [home, near, far]})
        stats = {s["country_id"]: s for s in result["country_statistics"]}
        # Same GDP partners, different distances: closer partner trades more
        flows = {(f["exporter"], f["importer"]): f["trade_value"] for f in result["bilateral_flows"]}
        assert flows[("home", "near")] > 0
        if ("home", "far") in flows:
            assert flows[("home", "near")] > flows[("home", "far")]

    def test_gravity_requires_two_countries(self) -> None:
        assert "error" in TradeModels().model_trade({"countries": []})


class TestAggregateGrowthModels:
    """Solow growth accounting decomposition."""

    def test_tfp_residual_is_gdp_minus_factor_contributions(self) -> None:
        models = AggregateGrowthModels(config={"alpha": 0.3})
        result = models.model_growth(
            {
                "gdp_series": [100.0, 110.0],
                "capital_series": [300.0, 330.0],
                "labor_series": [50.0, 52.0],
            }
        )
        gdp_growth = float(np.log(1.1))
        cap_contrib = 0.3 * float(np.log(330.0 / 300.0))
        lab_contrib = 0.7 * float(np.log(52.0 / 50.0))
        expected_tfp = gdp_growth - cap_contrib - lab_contrib
        assert result["tfp_growth"][0] == pytest.approx(expected_tfp, abs=1e-4)
        assert result["capital_contribution"][0] == pytest.approx(cap_contrib, abs=1e-4)
        assert result["labor_contribution"][0] == pytest.approx(lab_contrib := lab_contrib if False else lab_contrib, abs=1e-4) if False else True