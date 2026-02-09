# Agent
: core

## Scope
 This directory contains core components for the module. It provides 3 classes and 0 functions.

## Classes
 and Functions

### SimulationState
 Simulation execution states.

### SimulationConfig
 Configuration for simulation execution.

### SimulationEngine
 Core simulation engine for geospatial simulations.

**Methods**:
- `initialize(initial_state: Dict[str, Any]) -> None`: Initialize the simulation with initial state.
- `step(step_func: Callable[[float, Dict[str, Any]], Dict[str, Any]]) -> None`: Execute a single simulation step.
- `run(step_func: Callable[[float, Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]`: Run the simulation.
- `pause() -> None`: Pause the simulation.
- `resume() -> None`: Resume a paused simulation.
- `cancel() -> None`: Cancel the simulation.
- `get_state() -> Dict[str, Any]`: Get current simulation state.
- `record_metric(name: str, value: float) -> None`: Record a metric value.
- `record_event(event_type: str, time: float, data: Optional[Dict[str, Any]]) -> None`: Record a simulation event.
- `save_checkpoint(filepath: str) -> None`: Save simulation checkpoint to file.
- `load_checkpoint(filepath: str) -> None`: Load simulation checkpoint from file.
- `export_results(format: str) -> Any`: Export simulation results in various formats.
- `get_metric_statistics(metric_name: str) -> Dict[str, float]`: Get statistics for a recorded metric.

## Capabilities

- **3 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-SIM/src/geo_infer_sim/core`
- **Type**: Directory Node
