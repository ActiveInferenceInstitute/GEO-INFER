"""
Tests for the simulation engine.
"""

import pytest
import numpy as np
import tempfile
import os

from geo_infer_sim.core.simulation_engine import (
    SimulationEngine,
    SimulationConfig,
    SimulationState
)


class TestSimulationConfig:
    """Test suite for SimulationConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SimulationConfig()
        
        assert config.time_step == 1.0
        assert config.max_time == 100.0
        assert config.output_interval == 1.0
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SimulationConfig(
            time_step=0.5,
            max_time=50.0,
            random_seed=42
        )
        
        assert config.time_step == 0.5
        assert config.max_time == 50.0
        assert config.random_seed == 42
    
    def test_invalid_time_step(self):
        """Test validation of time_step."""
        with pytest.raises(ValueError):
            SimulationConfig(time_step=-1.0)
    
    def test_invalid_max_time(self):
        """Test validation of max_time."""
        with pytest.raises(ValueError):
            SimulationConfig(max_time=0)


class TestSimulationEngine:
    """Test suite for SimulationEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a simulation engine."""
        config = SimulationConfig(
            time_step=1.0,
            max_time=10.0,
            random_seed=42
        )
        return SimulationEngine(config)
    
    @pytest.fixture
    def step_func(self):
        """Simple step function for testing."""
        def step(time, state):
            return {
                "value": state.get("value", 0) + 1,
                "time": time
            }
        return step
    
    def test_init(self, engine):
        """Test engine initialization."""
        assert engine.state == SimulationState.INITIALIZED
        assert engine.current_time == 0.0
    
    def test_initialize(self, engine):
        """Test simulation initialization."""
        initial_state = {"value": 0}
        engine.initialize(initial_state)
        
        assert engine.state == SimulationState.INITIALIZED
        assert len(engine.state_history) == 1
    
    def test_step(self, engine, step_func):
        """Test single simulation step."""
        engine.initialize({"value": 0})
        engine.step(step_func)
        
        assert engine.state == SimulationState.RUNNING
        assert engine.current_time == 1.0
    
    def test_run(self, engine, step_func):
        """Test complete simulation run."""
        engine.initialize({"value": 0})
        results = engine.run(step_func)
        
        assert results["status"] == "completed"
        assert results["final_time"] == 10.0
    
    def test_pause_resume(self, engine):
        """Test pause and resume."""
        engine.initialize({"value": 0})
        engine.state = SimulationState.RUNNING
        
        engine.pause()
        assert engine.state == SimulationState.PAUSED
        
        engine.resume()
        assert engine.state == SimulationState.RUNNING
    
    def test_cancel(self, engine):
        """Test simulation cancellation."""
        engine.cancel()
        assert engine.state == SimulationState.CANCELLED
    
    def test_record_metric(self, engine):
        """Test metric recording."""
        engine.record_metric("test_metric", 1.0)
        engine.record_metric("test_metric", 2.0)
        
        assert len(engine.metrics["test_metric"]) == 2
    
    def test_record_event(self, engine):
        """Test event recording."""
        engine.record_event("test_event", 1.0, {"key": "value"})
        
        assert len(engine.events) == 1
        assert engine.events[0]["type"] == "test_event"
    
    def test_get_state(self, engine):
        """Test getting simulation state."""
        state = engine.get_state()
        
        assert "state" in state
        assert "current_time" in state
        assert "config" in state


class TestCheckpointing:
    """Test suite for checkpoint functionality."""
    
    @pytest.fixture
    def engine_with_history(self):
        """Create engine with simulation history."""
        engine = SimulationEngine(SimulationConfig(max_time=5.0))
        engine.initialize({"value": 0})
        
        def step(time, state):
            return {"value": state.get("value", 0) + 1}
        
        engine.run(step)
        return engine
    
    def test_save_checkpoint(self, engine_with_history):
        """Test saving checkpoint."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            engine_with_history.save_checkpoint(filepath)
            assert os.path.exists(filepath)
        finally:
            os.unlink(filepath)
    
    def test_load_checkpoint(self, engine_with_history):
        """Test loading checkpoint."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            engine_with_history.save_checkpoint(filepath)
            
            new_engine = SimulationEngine()
            new_engine.load_checkpoint(filepath)
            
            assert new_engine.current_time == engine_with_history.current_time
            assert len(new_engine.state_history) == len(engine_with_history.state_history)
        finally:
            os.unlink(filepath)


class TestResultsExport:
    """Test suite for results export functionality."""
    
    @pytest.fixture
    def engine_with_results(self):
        """Create engine with simulation results."""
        engine = SimulationEngine(SimulationConfig(max_time=5.0))
        engine.initialize({"value": 0, "rate": 0.1})
        
        def step(time, state):
            new_value = state.get("value", 0) + state.get("rate", 0)
            engine.record_metric("value", new_value)
            return {"value": new_value, "rate": state.get("rate", 0)}
        
        engine.run(step)
        return engine
    
    def test_export_dataframe(self, engine_with_results):
        """Test exporting results as DataFrame."""
        df = engine_with_results.export_results(format="dataframe")
        
        assert len(df) > 0
        assert "time" in df.columns
    
    def test_export_dict(self, engine_with_results):
        """Test exporting results as dict."""
        result = engine_with_results.export_results(format="dict")
        
        assert "state_history" in result
        assert "metrics" in result
        assert "events" in result
    
    def test_export_json(self, engine_with_results):
        """Test exporting results as JSON."""
        json_str = engine_with_results.export_results(format="json")
        
        assert isinstance(json_str, str)
        assert "state_history" in json_str


class TestMetricStatistics:
    """Test suite for metric statistics."""
    
    @pytest.fixture
    def engine_with_metrics(self):
        """Create engine with recorded metrics."""
        engine = SimulationEngine()
        
        # Record some metrics
        for i in range(10):
            engine.record_metric("increasing", float(i))
            engine.record_metric("decreasing", 10.0 - i)
            engine.record_metric("constant", 5.0)
        
        return engine
    
    def test_get_metric_statistics(self, engine_with_metrics):
        """Test getting metric statistics."""
        stats = engine_with_metrics.get_metric_statistics("increasing")
        
        assert stats["count"] == 10
        assert stats["min"] == 0.0
        assert stats["max"] == 9.0
        assert stats["trend"] == "increasing"
    
    def test_decreasing_trend(self, engine_with_metrics):
        """Test decreasing trend detection."""
        stats = engine_with_metrics.get_metric_statistics("decreasing")
        
        assert stats["trend"] == "decreasing"
    
    def test_stable_trend(self, engine_with_metrics):
        """Test stable trend detection."""
        stats = engine_with_metrics.get_metric_statistics("constant")
        
        assert stats["trend"] == "stable"
    
    def test_missing_metric(self, engine_with_metrics):
        """Test handling of missing metric."""
        stats = engine_with_metrics.get_metric_statistics("nonexistent")
        
        assert "error" in stats
