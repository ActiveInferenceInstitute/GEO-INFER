# Agent: core

## Scope

This directory contains core Active Inference components implementing the Free Energy Principle. It provides 10 classes implementing belief updating, policy selection, free energy calculation, generative models, and variational inference algorithms.

## Classes and Functions

### ActiveInferenceModel

Main class for active inference agents with support for nested models.

**Methods**:

- `set_generative_model(model: GenerativeModel)`: Set the generative model for this active inference agent.
- `perceive(observation: np.ndarray) -> np.ndarray`: Update beliefs based on new observation.
- `act(available_actions: Optional[List[Any]]) -> Any`: Select action based on expected free energy minimization.
- `update_observations(observations: Dict[str, Any]) -> None`: Update observations for the active inference model.
- `update_preferences(preferences: Dict[str, float]) -> None`: Update preferences for the active inference model.
- `update_with_outcome(decision: Dict[str, Any], outcome: Dict[str, Any]) -> None`: Update model based on decision and outcome.
- `generate_policies(available_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]`: Generate policy options from available actions.
- `select_policy(policies: List[Dict[str, Any]]) -> Dict[str, Any]`: Select optimal policy from candidates.
- `compute_expected_free_energy(policy: Dict[str, Any]) -> float`: Compute expected free energy for a policy.
- `step(observation: np.ndarray, available_actions: Optional[List[Any]], return_result: bool = False) -> Tuple[np.ndarray, Any] | ActiveInferenceStepResult`: Perform one complete active inference step.
- `compute_free_energy() -> float`: Compute current variational free energy.
- `reset()`: Reset the model to initial state.
- `get_history() -> List[Dict[str, Any]]`: Get the complete history of interactions.
- `get_current_state() -> Dict[str, Any]`: Get current model state.
- `apply_to_h3(h3_obs: Dict[str, np.ndarray])`: Update a spatial generative model from H3-indexed observations.
- `infer_over_h3_grid(h3_grid: Dict[str, Any])`: Run read-only one-step inference across an H3 observation grid.
- `set_preferences(preferences: Union[np.ndarray, Dict[str, Any]])`: Override prior preferences used during inference.

### BayesianBeliefUpdate

Bayesian belief updating for active inference models.

**Methods**:

- `update_categorical(prior_beliefs: np.ndarray, observation: np.ndarray, likelihood_matrix: np.ndarray) -> np.ndarray`: Update categorical beliefs using Bayes' rule.
- `update_gaussian(prior_mean: np.ndarray, prior_precision: np.ndarray, observation: np.ndarray, observation_matrix: np.ndarray, observation_precision: np.ndarray) -> Dict[str, np.ndarray]`: Update Gaussian beliefs using Kalman filter equations.
- `compute_prediction_error(prediction: np.ndarray, observation: np.ndarray, precision: float) -> float`: Compute precision-weighted prediction error.
- `compute_surprise(observation: np.ndarray, predicted_distribution: np.ndarray) -> float`: Compute surprise (negative log probability) of observation.
- `update_beliefs(prior_beliefs: np.ndarray, observation: np.ndarray, likelihood: np.ndarray) -> np.ndarray`: General belief update dispatching to categorical or gaussian.

### DynamicCausalModel

Dynamic Causal Model for continuous-time active inference.

**Methods**:

- `state_equation(state: np.ndarray, t: float, inputs: np.ndarray) -> np.ndarray`: State evolution equation: dx/dt = f(x, u, t).
- `observation_equation(state: np.ndarray) -> np.ndarray`: Observation equation: y = g(x) + noise.
- `integrate_dynamics(initial_state: np.ndarray, inputs: np.ndarray, time_points: np.ndarray) -> np.ndarray`: Integrate the system dynamics over time.
- `generate_observations(state_trajectory: np.ndarray) -> np.ndarray`: Generate observations from state trajectory.
- `estimate_parameters(observations: np.ndarray, inputs: np.ndarray, time_points: np.ndarray, initial_state: Optional[np.ndarray]) -> Dict[str, np.ndarray]`: Estimate model parameters from data.
- `set_parameters(A: np.ndarray, B: np.ndarray, C: np.ndarray)`: Set model parameters.
- `set_noise_parameters(Q: np.ndarray, R: np.ndarray)`: Set noise parameters.

### FreeEnergyCalculator

Calculator for variational free energy in active inference models.

**Methods**:

- `compute_categorical_free_energy(beliefs: np.ndarray, observations: np.ndarray, preferences: Optional[np.ndarray]) -> float`: Compute variational free energy for categorical models.
- `compute_gaussian_free_energy(mean: np.ndarray, precision: np.ndarray, observations: np.ndarray, prior_mean: Optional[np.ndarray], prior_precision: Optional[np.ndarray]) -> float`: Compute free energy for Gaussian models.
- `compute_expected_free_energy(beliefs: np.ndarray, policy: Dict[str, Any], preferences: Optional[np.ndarray]) -> float`: Compute expected free energy for policy evaluation.
- `compute(beliefs: Union[np.ndarray, Dict], observations: np.ndarray, preferences: np.ndarray, model_type: str) -> float`: General free energy compute dispatching.

### MarkovBlanket

Markov blanket specification for conditional independence.

**Methods**:

- `check_conditional_independence(state_idx: int, all_states: np.ndarray) -> bool`: Check if state satisfies conditional independence given Markov blanket.

### HierarchicalLevel

Specification for a level in hierarchical active inference.

### GenerativeModel

Generative model implementation for active inference.

**Methods**:

- `update_beliefs(observations: Dict[str, np.ndarray]) -> Dict[str, Any]`: Update beliefs using hierarchical inference and message passing.
- `compute_free_energy() -> float`: Compute variational free energy.
- `add_nested_level(child_model: 'GenerativeModel')`: Add a nested child model.
- `update_nested_beliefs(observations)`: Update beliefs through hierarchy recursively.
- `enable_spatial_navigation(grid_size: int)`: Enable spatial navigation mode for geospatial applications.
- `enable_h3_spatial(h3_resolution: int, boundary: Dict[str, Any])`: Enable H3-based spatial modeling.
- `integrate_rxinfer(model_specification: str, data: Dict[str, Any]) -> Dict[str, Any]`: Integrate with RxInfer for Factor Graph-based inference.
- `integrate_bayeux(log_density_fn: Callable, test_point: Dict[str, np.ndarray]) -> Dict[str, Any]`: Integrate with JAX-based Bayeux for scalable inference.
- `diffuse_beliefs(beliefs, diffusion_rate)`: Diffuse beliefs across spatial neighbors using precision-weighted averaging.
- `aggregate_beliefs_to_resolution(beliefs, target_resolution)`: Aggregate fine-resolution H3 beliefs to a coarser resolution.
- `set_preferences(preferences: Dict[str, np.ndarray]) -> None`: Set prior preferences with hierarchical support.
- `get_model_summary() -> Dict[str, Any]`: Get model summary for monitoring and debugging.
- `update_h3_beliefs(h3_observations: Dict[str, np.ndarray])`: Update H3-indexed beliefs and return spatial consistency diagnostics.

### MarkovDecisionProcess

Markov Decision Process implementation for active inference.

**Methods**:

- `get_transition_prob(state: int, action: int) -> np.ndarray`: Get transition probabilities for a given state and action.
- `get_observation_prob(state: int) -> np.ndarray`: Get observation probabilities for a given state.
- `transition(state: int, action: int) -> int`: Sample next state given current state and action.
- `observe(state: int) -> int`: Sample observation given current state.
- `simulate(initial_state: int, policy: Union[List[int], np.ndarray], stochastic: bool) -> Tuple[List[int], List[int]]`: Simulate a trajectory through the MDP following a policy.
- `get_predictive_state(belief: np.ndarray, action: int) -> np.ndarray`: Get predictive state distribution after an action.
- `get_predictive_observation(state_dist: np.ndarray) -> np.ndarray`: Get predictive observation distribution given a state distribution.
- `update_belief(prior_belief: np.ndarray, observation: int) -> np.ndarray`: Update belief distribution using Bayes' rule.
- `set_transition_matrix(state: int, action: int, distribution: np.ndarray) -> None`: Set transition distribution for a specific state-action pair.
- `set_observation_matrix(state: int, distribution: np.ndarray) -> None`: Set observation distribution for a specific state.

### PolicySelector

Policy selector for active inference models.

**Methods**:

- `select_policy(beliefs: np.ndarray, policies: List[Dict[str, Any]], preferences: Optional[np.ndarray]) -> Dict[str, Any]`: Select a policy based on expected free energy.
- `compute_expected_free_energy(beliefs: np.ndarray, policy: Dict[str, Any], preferences: Optional[np.ndarray]) -> float`: Compute expected free energy for a policy.
- `compute_policy_precision(expected_free_energies: np.ndarray, baseline_precision: float) -> float`: Compute precision parameter for policy distribution.
- `evaluate_policy_set(beliefs: np.ndarray, policies: List[Dict[str, Any]], preferences: Optional[np.ndarray]) -> Dict[str, Any]`: Evaluate a set of policies without selection.
- `select_action(beliefs: np.ndarray, available_actions: List[Any], generative_model: Any) -> Any`: Select a single action based on current beliefs.

### VariationalInference

Variational inference engine for active inference models.

**Methods**:

- `mean_field_update(prior: Dict[str, np.ndarray], likelihood: Dict[str, np.ndarray], observations: np.ndarray) -> Dict[str, np.ndarray]`: Perform mean-field variational inference update.
- `mean_field_update_categorical(prior: np.ndarray, likelihood: np.ndarray, observations: np.ndarray) -> np.ndarray`: Update categorical mean-field beliefs from a Dirichlet prior.
- `mean_field_update_gaussian(mean: np.ndarray, cov: np.ndarray, obs: np.ndarray) -> np.ndarray`: Update Gaussian mean-field beliefs and return the posterior mean.
- `structured_update(factor_graph: Dict[str, Any], observations: Dict[str, np.ndarray], method: str) -> Dict[str, np.ndarray]`: Perform structured variational inference with factor graphs.
- `importance_sampling_update(prior: Dict[str, np.ndarray], likelihood_fn: callable, observations: np.ndarray, n_samples: int) -> Dict[str, np.ndarray]`: Perform importance sampling for posterior approximation.
- `compute_elbo(posterior: Dict[str, np.ndarray], prior: Dict[str, np.ndarray], likelihood: Dict[str, np.ndarray], observations: np.ndarray) -> float`: Compute Evidence Lower BOund (ELBO).

## Capabilities

- **Active Inference Modeling**: Core `ActiveInferenceModel` class orchestrating perception-action loops
- **Belief Updating**: Bayesian belief updating for categorical and Gaussian models
- **Free Energy Calculation**: Variational free energy computation for policy evaluation
- **Generative Models**: Hierarchical generative models with Markov blankets and spatial extensions
- **Policy Selection**: Expected free energy minimization for action selection
- **Variational Inference**: Mean-field and structured variational inference methods
- **MDP Modeling**: Markov Decision Process implementation for discrete state spaces
- **Dynamic Causal Modeling**: Continuous-time active inference with DCM

## Integration

- **Location**: `GEO-INFER-ACT/src/geo_infer_act/core`
- **Type**: Core Module Component
- **Dependencies**: `numpy`, `scipy`, `geo_infer_act.utils.math` for mathematical utilities
- **Used By**: 
 
- `geo_infer_act.models` for domain-specific models
 
- `geo_infer_act.api` for API interfaces
 
- `geo_infer_agent` for agent implementations
- **Provides**: Core Active Inference algorithms and models for the GEO-INFER framework

---

This AGENTS.md documents core Active Inference components for GEO-INFER-ACT.
