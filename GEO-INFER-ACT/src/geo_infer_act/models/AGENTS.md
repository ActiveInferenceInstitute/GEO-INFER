# Agent: models

## Scope

This directory contains domain-specific Active Inference models for ecological, climate, urban, resource, and multi-agent applications. It provides 8 classes implementing specialized generative models for different problem domains.

## Classes and Functions

### ActiveInferenceModel

Base class for active inference models.

**Methods**:

- `step(actions: Optional[Any]) -> Any`: Advance the model by one step.
- `reset() -> Any`: Reset the model to initial state.

### CategoricalModel

Categorical active inference model.

**Methods**:

- `set_preferences(preferences: np.ndarray) -> None`: Set preference distribution.
- `set_transition_matrix(transition_matrix: np.ndarray) -> None`: Set state transition matrix.
- `set_likelihood_matrix(likelihood_matrix: np.ndarray) -> None`: Set observation likelihood matrix.
- `update_beliefs(observation: np.ndarray) -> np.ndarray`: Update beliefs given observation.
- `step(action: Optional[int]) -> np.ndarray`: Advance the model by one step.
- `reset() -> np.ndarray`: Reset beliefs to uniform distribution.
- `compute_free_energy() -> float`: 

### GaussianModel

Gaussian active inference model.

**Methods**:

- `set_preferences(mean: np.ndarray, cov: np.ndarray) -> None`: Set preference distribution.
- `set_transition_model(A: np.ndarray, B: Optional[np.ndarray], Q: Optional[np.ndarray]) -> None`: Set transition model parameters.
- `set_observation_model(C: np.ndarray, R: Optional[np.ndarray]) -> None`: Set observation model parameters.
- `update_beliefs(observation: np.ndarray) -> Dict[str, np.ndarray]`: Update beliefs given observation (Kalman filter).
- `step(control: Optional[np.ndarray]) -> Dict[str, np.ndarray]`: Advance the model by one step.
- `reset() -> Dict[str, np.ndarray]`: Reset beliefs to initial state.

### ClimateModel

Climate adaptation modeling using Active Inference.

**Methods**:

- `step(observations)`: Execute one step of active inference.

### EcologicalModel

Ecological niche modeling using Active Inference.

**Methods**:

- `step(observation: List[int])`: Advance the ecological model by one step.

### MultiAgentModel

Multi-agent coordination using active inference.

**Methods**:

- `step(actions: Optional[List[Dict[str, Any]]]) -> Tuple[Dict[str, Any], bool]`: 
- `enable_h3_spatial(resolution: int, boundary: Dict[str, Any])`: Enable H3 spatial modeling for multi-agent active inference.
- `simulate_h3_lattice(timesteps: int, obs_gen: Callable[[str], np.ndarray]) -> List[Dict[str, Dict]]`: Simulate active inference on H3 lattice with proper perception-action loops.
- `coordinate_agents() -> Dict[str, Any]`: Coordinate agents through message passing and shared information.
- `get_agent_messages(agent_id)`: 

### ResourceModel

Resource allocation modeling using active inference.

**Methods**:

- `step(actions) -> Tuple[Dict[str, Any], bool]`: 

### UrbanModel

Urban planning model using active inference.

**Methods**:

- `step(input_actions)`: Advance one simulation step.
- `run_simulation(n_steps: int)`: 

## Capabilities

- **8 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-ACT/src/geo_infer_act/models`
- **Type**: Module Component
- **Dependencies**: `geo_infer_act.core` for core Active Inference functionality
- **Used By**: 
 
- `geo_infer_act.api` for API interfaces
 
- `geo_infer_act.examples` for demonstration
  - Domain modules (AG, FOREST, CLIMATE) for specialized applications
