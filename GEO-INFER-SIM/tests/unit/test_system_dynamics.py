"""Unit tests for the SystemDynamicsModel paradigm (M8-01).

Covers stock/flow wiring, flow-rate resolution, integration with
clamping, conservation across unbounded flows, reset determinism and
flow validation errors.
"""

import pytest

from geo_infer_sim.paradigms.system_dynamics import Flow, Stock, SystemDynamicsModel


def _two_stock_model(min_source=None, max_target=None) -> SystemDynamicsModel:
    model = SystemDynamicsModel()
    model.add_stock("reservoir", 100.0, min_value=min_source)
    model.add_stock("pond", 0.0, max_value=max_target)
    model.add_flow(
        "drain", source_stock="reservoir", target_stock="pond", constant_rate=2.0
    )
    return model


class TestStockAndFlowSetup:
    """Stock init and flow validation."""

    def test_stock_current_value_initializes_to_initial_value(self) -> None:
        stock = Stock(name=" biomass ", initial_value=42.0)
        assert stock.current_value == 42.0

    def test_flow_requires_rate_or_constant(self) -> None:
        model = SystemDynamicsModel()
        with pytest.raises(ValueError, match="rate_function or constant_rate"):
            model.add_flow("broken", source_stock="a", target_stock="b")

    def test_calculate_flow_rate_resolution(self) -> None:
        model = SystemDynamicsModel()
        constant = Flow(name="c", constant_rate=3.5)
        assert model.calculate_flow_rate(constant, {}) == 3.5

        proportional = Flow(
            name="p",
            rate_function=lambda stocks: 0.1 * stocks["reservoir"],
        )
        assert model.calculate_flow_rate(proportional, {"reservoir": 100.0}) == 10.0

        inert = Flow(name="i")
        assert model.calculate_flow_rate(inert, {}) == 0.0


class TestIntegration:
    """step() integrates flows into stocks."""

    def test_unbounded_flow_conserves_total(self) -> None:
        model = _two_stock_model()
        model.step(time_step=0.5)

        assert model.stocks["reservoir"].current_value == pytest.approx(99.0)
        assert model.stocks["pond"].current_value == pytest.approx(1.0)
        # Nothing is created or destroyed when no bounds bind.
        total = sum(s.current_value for s in model.stocks.values())
        assert total == pytest.approx(100.0)
        assert model.time == 0.5
        assert model.history[-1] == {"time": 0.5, "reservoir": 99.0, "pond": 1.0}

    def test_rate_function_uses_current_stock_values(self) -> None:
        """Proportional outflow: rate = 0.1 × source evaluated before the step."""
        model = SystemDynamicsModel()
        model.add_stock("population", 200.0)
        model.add_stock("migrated", 0.0)
        model.add_flow(
            "emigration",
            source_stock="population",
            target_stock="migrated",
            rate_function=lambda stocks: 0.1 * stocks["population"],
        )
        model.step(time_step=1.0)

        assert model.stocks["population"].current_value == pytest.approx(180.0)
        assert model.stocks["migrated"].current_value == pytest.approx(20.0)

    def test_min_bound_clamps_source_at_zero(self) -> None:
        model = _two_stock_model(min_source=0.0)
        model.add_flow(
            "big_drain",
            source_stock="reservoir",
            target_stock="pond",
            constant_rate=150.0,
        )
        model.step(time_step=1.0)  # drain 2 + big_drain 150 = 152 outflow

        assert model.stocks["reservoir"].current_value == pytest.approx(0.0)
        assert model.stocks["reservoir"].current_value >= 0.0

    def test_max_bound_clamps_target(self) -> None:
        model = _two_stock_model(max_target=1.5)
        model.step(time_step=1.0)  # pond would reach 2.0 without the bound

        assert model.stocks["pond"].current_value == pytest.approx(1.5)

    def test_get_state_reports_stock_values(self) -> None:
        model = _two_stock_model()
        model.step(time_step=1.0)
        state = model.get_state()

        assert state["time"] == 1.0
        assert state["stocks"] == {"reservoir": 98.0, "pond": 2.0}
        assert state["history"] == model.history[-100:]


class TestReset:
    """reset() restores initial values, time and history."""

    def test_reset_restores_initial_state(self) -> None:
        model = _two_stock_model()
        for _ in range(5):
            model.step(time_step=1.0)
        assert model.time == 5.0
        assert model.stocks["reservoir"].current_value == pytest.approx(90.0)

        model.reset()

        assert model.time == 0.0
        assert model.history == []
        assert model.stocks["reservoir"].current_value == pytest.approx(100.0)
        assert model.stocks["pond"].current_value == pytest.approx(0.0)

        # The reset model integrates identically to a fresh one.
        model.step(time_step=1.0)
        fresh = _two_stock_model()
        fresh.step(time_step=1.0)
        assert model.stocks["reservoir"].current_value == (
            fresh.stocks["reservoir"].current_value
        )
        assert model.stocks["pond"].current_value == fresh.stocks["pond"].current_value
