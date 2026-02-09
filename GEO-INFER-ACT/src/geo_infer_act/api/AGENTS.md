# Agent
: api

## Scope
 This directory contains api components for the module. It provides 2 classes and 1 functions.

## Classes
 and Functions

### Client
 REST API client for GEO-INFER-ACT.

**Methods**:
- `create_model(model_config: Dict[str, Any]) -> Dict[str, Any]`: Create a model via API.
- `get_model(model_id: str) -> Dict[str, Any]`: Get model details via API.

### ActiveInferenceInterface
 High-level interface for active inference models.

**Methods**:
- `create_model(model_id: str, model_type: str, parameters: Dict[str, Any]) -> None`: Create a active inference model.
- `update_beliefs(model_id: str, observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]`: Update model beliefs based on observations.
- `select_policy(model_id: str) -> Dict[str, Any]`: Select optimal policy based on current beliefs.
- `set_preferences(model_id: str, preferences: Dict[str, Any]) -> None`: Set prior preferences for the model.
- `get_free_energy(model_id: str) -> float`: Calculate free energy for the current model state.

### create_endpoints
 `create_endpoints()` Create API endpoint definitions.

## Capabilities

- **2 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-ACT/src/geo_infer_act/api`
- **Type**: Directory Node
