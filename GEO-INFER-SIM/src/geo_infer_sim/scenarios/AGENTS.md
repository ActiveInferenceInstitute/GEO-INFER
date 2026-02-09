# Agent
: scenarios

## Scope
 This directory contains scenarios components for the module. It provides 2 classes and 0 functions.

## Classes
 and Functions

### Scenario
 Represents a simulation scenario.

### ScenarioManager
 Manager for simulation scenarios.

**Methods**:
- `create_scenario(name: str, description: str, parameters: Optional[Dict[str, Any]], initial_conditions: Optional[Dict[str, Any]], interventions: Optional[List[Dict[str, Any]]], scenario_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> Scenario`: Create a simulation scenario.
- `get_scenario(scenario_id: str) -> Optional[Scenario]`: Get a scenario by ID.
- `list_scenarios() -> List[Scenario]`: List all scenarios.
- `update_scenario(scenario_id: str, name: Optional[str], description: Optional[str], parameters: Optional[Dict[str, Any]], initial_conditions: Optional[Dict[str, Any]], interventions: Optional[List[Dict[str, Any]]]) -> bool`: Update an existing scenario.
- `delete_scenario(scenario_id: str) -> bool`: Delete a scenario.
- `save_scenario_result(scenario_id: str, result: Dict[str, Any]) -> None`: Save results for a scenario.
- `get_scenario_result(scenario_id: str) -> Optional[Dict[str, Any]]`: Get results for a scenario.
- `compare_scenarios(scenario_ids: List[str], metrics: Optional[List[str]]) -> Dict[str, Any]`: Compare multiple scenarios.
- `run_scenarios(scenario_ids: List[str], simulation_func: Any, parallel: bool) -> Dict[str, Dict[str, Any]]`: Run multiple scenarios using a simulation function.
- `analyze_results(scenario_ids: Optional[List[str]]) -> Dict[str, Any]`: Analyze results across scenarios.

## Capabilities

- **2 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-SIM/src/geo_infer_sim/scenarios`
- **Type**: Directory Node
