"""
Unit tests for simulation engine.
"""

import pytest
from geo_infer_sim.core.simulation_engine import (
    SimulationEngine,
    SimulationConfig,
    SimulationState,
)
from geo_infer_sim.module_simulations import ModuleSimulationConfig, ModuleSimulations


class TestSimulationEngine:
    """Test SimulationEngine class."""

    @pytest.fixture
    def engine(self) -> SimulationEngine:
        """Create a simulation engine instance."""
        config = SimulationConfig(time_step=1.0, max_time=10.0)
        return SimulationEngine(config)

    def test_initialize(self, engine: SimulationEngine) -> None:
        """Test simulation initialization."""
        initial_state = {"population": 100, "resources": 50}
        engine.initialize(initial_state)

        assert engine.state == SimulationState.INITIALIZED
        assert engine.current_time == 0.0
        assert len(engine.state_history) == 1

    def test_step(self, engine: SimulationEngine) -> None:
        """Test simulation step execution."""
        initial_state = {"value": 10}
        engine.initialize(initial_state)

        def step_func(time, state):
            return {"value": state["value"] + 1}

        engine.step(step_func)

        assert engine.current_time == 1.0
        assert engine.state == SimulationState.RUNNING

    def test_run(self, engine: SimulationEngine) -> None:
        """Test complete simulation run."""
        initial_state = {"counter": 0}
        engine.initialize(initial_state)

        def step_func(time, state):
            return {"counter": state["counter"] + 1}

        results = engine.run(step_func)

        assert results["status"] == SimulationState.COMPLETED.value
        assert results["final_time"] == 10.0
        assert "state_history" in results

    def test_pause_resume(self, engine: SimulationEngine) -> None:
        """Test pause and resume functionality."""
        initial_state = {"value": 0}
        engine.initialize(initial_state)

        engine.state = SimulationState.RUNNING
        engine.pause()

        assert engine.state == SimulationState.PAUSED

        engine.resume()

        assert engine.state == SimulationState.RUNNING

    def test_record_metric(self, engine: SimulationEngine) -> None:
        """Test metric recording."""
        engine.record_metric("test_metric", 42.0)

        assert "test_metric" in engine.metrics
        assert engine.metrics["test_metric"] == [42.0]

    def test_ant_simulation_updates_pheromone_trails(self) -> None:
        simulations = ModuleSimulations(
            ModuleSimulationConfig(time_horizon=1.0, time_step=1.0, random_seed=42)
        )

        result = simulations.simulate_ant(colony_size=2)

        assert result["module"] == "ANT"
        assert len(result["trail_history"]) == 1
        assert result["final_trails"].sum() > 0
