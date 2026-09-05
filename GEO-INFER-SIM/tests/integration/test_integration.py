"""
Integration tests for GEO-INFER-SIM.

Exercises the real cross-component path: ScenarioManager drives
SimulationEngine over multiple scenarios with distinct seeds and compares
results.
"""

import numpy as np

from geo_infer_sim.core.simulation_engine import SimulationConfig, SimulationEngine
from geo_infer_sim.scenarios.scenario_manager import ScenarioManager


def _run_scenario(scenario) -> dict:
    """Simulation function used by the ScenarioManager batch run."""
    engine = SimulationEngine(
        SimulationConfig(
            time_step=1.0,
            max_time=scenario.parameters["max_time"],
            random_seed=scenario.parameters["seed"],
        )
    )
    engine.initialize({"population": scenario.initial_conditions["population"]})

    population = scenario.initial_conditions["population"]

    def step_fn(time: float, state: dict) -> dict:
        nonlocal population
        population = state["population"] + int(engine.rng.integers(-1, 2))
        return {"population": population}

    while engine.current_time < engine.config.max_time:
        engine.step(step_fn)

    return {
        "scenario_id": scenario.scenario_id,
        "final_population": population,
    }


class TestSimIntegration:
    """Test simulation module integration."""

    def test_scenario_manager_drives_engine_end_to_end(self) -> None:
        """ScenarioManager runs Scenario-driven SimulationEngine runs and
        compares them across seeds."""
        manager = ScenarioManager()
        base = manager.create_scenario(
            name="baseline",
            description="no intervention",
            initial_conditions={"population": 100},
            parameters={"max_time": 10.0, "seed": 42},
        )
        alt = manager.create_scenario(
            name="high-growth",
            description="different seed",
            initial_conditions={"population": 100},
            parameters={"max_time": 10.0, "seed": 7},
        )

        results = manager.run_scenarios(
            [base.scenario_id, alt.scenario_id], _run_scenario, parallel=False
        )

        assert set(results) == {base.scenario_id, alt.scenario_id}
        assert all("error" not in r for r in results.values())
        assert results[base.scenario_id]["scenario_id"] == base.scenario_id

        # Same scenario re-run with the same seed reproduces bit-for-bit;
        # a different seed yields a different trajectory.
        repeat = _run_scenario(manager.scenarios[base.scenario_id])
        assert repeat == results[base.scenario_id]
        assert (
            results[alt.scenario_id]["final_population"]
            != results[base.scenario_id]["final_population"]
        )

    def test_parallel_scenario_failure_is_reported_not_silent(self) -> None:
        """A failing scenario surfaces as an {'error': ...} result entry in
        parallel batch execution instead of vanishing."""
        manager = ScenarioManager()
        good = manager.create_scenario(
            name="good", initial_conditions={}, parameters={}
        )
        bad = manager.create_scenario(
            name="bad", initial_conditions={}, parameters={}
        )

        def sim_func(scenario):
            if scenario.name == "bad":
                raise RuntimeError("boom")
            return {"ok": True}

        results = manager.run_scenarios(
            [good.scenario_id, bad.scenario_id], sim_func, parallel=True
        )
        assert results[good.scenario_id] == {"ok": True}
        assert "error" in results[bad.scenario_id]
