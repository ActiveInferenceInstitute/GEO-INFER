# Agent: utils

## Scope

This directory contains utility functions and helper classes for Active Inference analysis, visualization, mathematical operations, configuration management, and integration with other GEO-INFER modules. It provides 10 classes and 57 functions supporting core Active Inference operations.

## Classes and Functions

### ActiveInferenceAnalyzer

Analyzer for Active Inference model behavior.

**Methods**:

- `record_step(beliefs: np.ndarray, observations: np.ndarray, actions: Any, policies: Dict[str, Any], free_energy: float, metrics: Optional[Dict[str, Any]], timestamp: Optional[float])`: Record a single Active Inference step for analysis.
- `step_history() -> List[Dict[str, Any]]`: Return a list of step dictionaries for backward compatibility and easy iteration.
- `analyze_perception_patterns() -> Dict[str, Any]`: Analyze perception (belief updating) patterns.
- `analyze_action_selection_patterns() -> Dict[str, Any]`: Analyze action selection (policy inference) patterns.
- `analyze_free_energy_patterns() -> Dict[str, Any]`: Analyze Variational Free Energy patterns and dynamics.
- `save_traces_to_csv()`: Save all traces to CSV files for external analysis.
- `generate_comprehensive_report() -> str`: Generate analysis report.

### EnvironmentalState

Represents environmental state at a spatial location.

### ResourceAllocation

Represents resource allocation decision.

### SpatialPrediction

Spatial prediction with uncertainty quantification.

### EnvironmentalActiveInferenceEngine

Environmental Active Inference Engine for geospatial modeling.

**Methods**:

- `initialize_spatial_domain(boundary: Dict[str, Any]) -> None`: Initialize spatial domain using H3 hexagonal grid.
- `observe_environment(observations: Dict[str, Dict[str, float]], timestamp: float) -> None`: Update environmental state beliefs based on new observations.
- `predict_environmental_dynamics(forecast_timesteps: int) -> Dict[str, List[SpatialPrediction]]`: Predict future environmental states using learned dynamics.
- `optimize_resource_allocation(resource_budget: float, resource_types: List[str], optimization_objective: str) -> List[ResourceAllocation]`: Optimize resource allocation using active inference principles.
- `analyze_environmental_uncertainty() -> Dict[str, Any]`: Analyze environmental uncertainty across the spatial domain.
- `compute_environmental_free_energy() -> Dict[str, float]`: Compute environmental free energy across the spatial domain.
- `get_environmental_summary() -> Dict[str, Any]`: Get summary of environmental state and analysis.

### MultiScaleHierarchicalAnalyzer

Multi-scale hierarchical analyzer for geospatial active inference.

**Methods**:

- `initialize_hierarchy(boundary: Dict[str, Any]) -> None`: Initialize hierarchical structure.
- `propagate_beliefs_hierarchically(bottom_up_evidence: Dict[str, Dict[str, np.ndarray]], top_down_priors: Dict[str, Dict[str, np.ndarray]]) -> Dict[str, Dict[str, np.ndarray]]`: Propagate beliefs hierarchically using message passing.
- `analyze_cross_scale_interactions() -> Dict[str, Any]`: Analyze interactions across different spatial scales.
- `detect_emergent_patterns() -> List[Dict[str, Any]]`: Detect emergent spatial patterns across hierarchical levels.

### H3SpatialGraph

### LevelSpatialGraph

### ModernToolsIntegration

Integration hub for modern Active Inference tools and frameworks.

**Methods**:

- `create_rxinfer_model(model_spec: str, data: Dict[str, Any]) -> Dict[str, Any]`: Create and run RxInfer model for constrained Bayesian inference.
- `create_bayeux_model(log_density_fn: str, test_point: Dict[str, Any], transform_fn: Optional[str]) -> Dict[str, Any]`: Create and optimize Bayeux model for scalable inference.
- `create_pymdp_agent(num_obs: List[int], num_states: List[int], A: Optional[np.ndarray], B: Optional[np.ndarray]) -> Dict[str, Any]`: Create pymdp agent for discrete Active Inference.
- `create_pymc_model(model_spec: str, data: Dict[str, Any]) -> Dict[str, Any]`: Create PyMC model for Bayesian inference.
- `create_pyro_model(model_fn: str, guide_fn: str, data: Dict[str, Any]) -> Dict[str, Any]`: Create Pyro model for deep probabilistic programming.

### IntegrationUtils

Utility class for integrating with other modules and tools.

**Methods**:

- `get_modern_tools()`: Get available modern tools integration.
- `integrate_with_space(spatial_data: Dict[str, Any]) -> Dict[str, Any]`: Integrate with GEO-INFER-SPACE module.
- `integrate_with_time(temporal_data: Dict[str, Any]) -> Dict[str, Any]`: Integrate with GEO-INFER-TIME module.
- `create_multi_agent_system(agent_configs: List[Dict[str, Any]]) -> Dict[str, Any]`: Create and coordinate a multi-agent system.

### create_shared_visualizations

`create_shared_visualizations(analyzer: ActiveInferenceAnalyzer) -> None`

Create shared visualizations for Active Inference analysis.

### create_belief_heatmap

`create_belief_heatmap(beliefs: List[np.ndarray], output_dir: Path)`

Create a heatmap of belief evolution over time.

### create_free_energy_plots

`create_free_energy_plots(free_energies: List[float], output_dir: Path)`

Create free energy analysis plots.

### create_policy_plots

`create_policy_plots(policies: List[Dict[str, Any]], output_dir: Path)`

Create policy analysis plots.

### create_correlation_analysis

`create_correlation_analysis(traces: Dict[str, List], output_dir: Path)`

Create correlation analysis between different traces.

### load_config

`load_config(path: str) -> Dict[str, Any]`

Load configuration from a YAML file.

### save_config

`save_config(config: Dict[str, Any], path: str) -> None`

Save configuration to a YAML file.

### merge_configs

`merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]`

Merge two configuration dictionaries, with override taking precedence.

### get_config_value

`get_config_value(config: Dict[str, Any], path: str, default: Optional[Any]) -> Any`

Get a configuration value using a dot-notated path.

### analyze_multi_scale_patterns

`analyze_multi_scale_patterns(hierarchical_graphs: Dict[str, Any], hierarchical_beliefs: Dict[str, Dict[str, np.ndarray]]) -> Dict[str, Any]`

Analyze multi-scale patterns in hierarchical belief structures.

### initialize_logger

`initialize_logger()`

Initialize module logger.

### integrate_rxinfer

`integrate_rxinfer(config: Dict[str, Any], model_params: Dict[str, Any]) -> Dict[str, Any]`

Integrate with RxInfer for scalable nested inference.

### integrate_bayeux

`integrate_bayeux(config: Dict[str, Any], model_params: Dict[str, Any]) -> Dict[str, Any]`

Integrate with Bayeux for JAX-based scalable inference.

### integrate_pymdp

`integrate_pymdp(config: Dict[str, Any], model_params: Dict[str, Any]) -> Dict[str, Any]`

Integrate with pymdp for discrete Active Inference.

### integrate_space

`integrate_space(config: Dict[str, Any], data: Optional[Dict[str, Any]]) -> Dict[str, Any]`

Integrate with GEO-INFER-SPACE module.

### integrate_time

`integrate_time(config: Dict[str, Any], data: Optional[Dict[str, Any]]) -> Dict[str, Any]`

Integrate with GEO-INFER-TIME module.

### integrate_sim

`integrate_sim(config: Dict[str, Any], data: Optional[Dict[str, Any]]) -> Dict[str, Any]`

Integrate with GEO-INFER-SIM module.

### create_h3_spatial_model

`create_h3_spatial_model(config: Dict[str, Any], h3_resolution: int, boundary: Dict[str, Any]) -> Dict[str, Any]`

Create H3-based spatial Active Inference model.

### coordinate_multi_agent_system

`coordinate_multi_agent_system(config: Dict[str, Any], agents: List[Dict[str, Any]], environment: Dict[str, Any]) -> Dict[str, Any]`

Coordinate multiple Active Inference agents.

### softmax

`softmax(x: np.ndarray, temperature: float, axis: int) -> np.ndarray`

Compute softmax transformation of input array.

### normalize_distribution

`normalize_distribution(x: np.ndarray, axis: int) -> np.ndarray`

Normalize array to form a probability distribution.

### kl_divergence

`kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float) -> float`

Compute Kullback-Leibler divergence between two probability distributions.

### entropy

`entropy(p: np.ndarray, base: Union[float, str]) -> float`

Compute entropy of a probability distribution.

### mutual_information

`mutual_information(joint: np.ndarray) -> float`

Compute mutual information from joint probability distribution.

### precision_weighted_error

`precision_weighted_error(mean: np.ndarray, target: np.ndarray, precision: np.ndarray) -> float`

Compute precision-weighted prediction error.

### gaussian_log_likelihood

`gaussian_log_likelihood(x: np.ndarray, mean: np.ndarray, precision: np.ndarray) -> float`

Compute log likelihood of Gaussian distribution.

### categorical_log_likelihood

`categorical_log_likelihood(observations: np.ndarray, probabilities: np.ndarray) -> float`

Compute log likelihood for categorical distribution.

### dirichlet_kl_divergence

`dirichlet_kl_divergence(alpha1: np.ndarray, alpha2: np.ndarray) -> float`

Compute KL divergence between two Dirichlet distributions.

### sample_categorical

`sample_categorical(probabilities: np.ndarray, n_samples: int, random_state: Optional[int]) -> np.ndarray`

Sample from categorical distribution.

### compute_free_energy_categorical

`compute_free_energy_categorical(beliefs: np.ndarray, observations: np.ndarray, prior: Optional[np.ndarray]) -> float`

Compute variational free energy for categorical models.

### compute_expected_free_energy

`compute_expected_free_energy(beliefs: np.ndarray, preferences: np.ndarray, exploration_bonus: float) -> float`

Compute expected free energy for policy evaluation.

### numerical_gradient

`numerical_gradient(func, x: np.ndarray, h: float) -> np.ndarray`

Compute numerical gradient using finite differences.

### stable_log_sum_exp

`stable_log_sum_exp(x: np.ndarray, axis: int) -> np.ndarray`

Compute log(sum(exp(x))) in a numerically stable way.

### matrix_log_det

`matrix_log_det(matrix: np.ndarray) -> float`

Compute log determinant of a matrix safely.

### detect_stationarity

`detect_stationarity(data: np.ndarray, window_size: int) -> Dict[str, float]`

Detect stationarity in time series data.

### detect_periodicity

`detect_periodicity(data: np.ndarray, min_period: int) -> Dict[str, Union[bool, float, int]]`

Detect periodic patterns in data.

### assess_complexity

`assess_complexity(data: np.ndarray) -> Dict[str, float]`

Assess complexity of data using multiple metrics.

### compute_prediction_accuracy

`compute_prediction_accuracy(predictions: np.ndarray, targets: np.ndarray) -> Dict[str, float]`

Compute various prediction accuracy metrics.

### compute_information_gain

`compute_information_gain(prior_entropy: float, posterior_entropy: float) -> float`

Compute information gain from prior to posterior.

### compute_surprise

`compute_surprise(observation: np.ndarray, predicted_distribution: np.ndarray, sigma: float) -> float`

Compute surprise of an observation given predicted distribution.

### assess_convergence

`assess_convergence(sequence: np.ndarray, window_size: int, threshold: float) -> Dict[str, Union[bool, float, int]]`

Assess convergence of a sequence.

### sample_dirichlet

`sample_dirichlet(alpha: np.ndarray) -> np.ndarray`

Sample from Dirichlet distribution.

### plot_belief_update

`plot_belief_update(beliefs_before: Dict[str, np.ndarray], beliefs_after: Dict[str, np.ndarray], state_labels: Optional[List[str]], title: str, figsize: Tuple[int, int]) -> plt.Figure`

Plot belief updates.

### plot_free_energy

`plot_free_energy(free_energy_history: List[float], iterations: Optional[List[int]], title: str, figsize: Tuple[int, int]) -> plt.Figure`

Plot free energy evolution.

### plot_policies

`plot_policies(policy_probabilities: np.ndarray, policy_labels: Optional[List[str]], expected_free_energies: Optional[np.ndarray], title: str, figsize: Tuple[int, int]) -> plt.Figure`

Plot policy analysis with enhanced visualization.

### plot_perception_analysis

`plot_perception_analysis(beliefs_history: List[np.ndarray], observations_history: List[np.ndarray], output_dir: Path, title: str) -> None`

Create perception analysis plots.

### plot_action_analysis

`plot_action_analysis(policy_history: List[Dict[str, Any]], action_history: List[Any], output_dir: Path, title: str) -> None`

Create action selection analysis plots.

### create_interpretability_dashboard

`create_interpretability_dashboard(analyzer, output_dir: Path)`

Create interpretability dashboard.

### plot_hierarchical_beliefs

`plot_hierarchical_beliefs(beliefs: Dict[str, np.ndarray]) -> plt.Figure`

Plot beliefs across hierarchical levels.

### plot_markov_blanket

`plot_markov_blanket(blanket: Dict[str, List[int]]) -> plt.Figure`

Plot Markov blanket structure.

### plot_h3_grid_static

`plot_h3_grid_static(h3_data: Dict[str, Dict], metric: str, title: str) -> plt.Figure`

Create static plot of H3 grid data.

### create_h3_gif

`create_h3_gif(history: List[Dict[str, Dict]], output_path: str, metric: str)`

Create animated GIF of H3 grid evolution over time.

### create_interactive_h3_slider

`create_interactive_h3_slider(history: List[Dict[str, Dict]], metric: str) -> Any`

Create interactive slider plot for H3 grid evolution.

## Capabilities

- **Analysis**: `ActiveInferenceAnalyzer` for model behavior analysis
- **Visualization**: Plotting and dashboard creation for beliefs, free energy, policies, and H3 spatial data
- **Mathematical Utilities**: Probability distributions, information theory, numerical methods
- **Configuration Management**: YAML config loading, saving, and merging
- **Integration**: Tools for integrating with GEO-INFER-SPACE, GEO-INFER-TIME, and modern inference frameworks (RxInfer, Bayeux, PyMDP)
- **Geospatial Active Inference**: Environmental modeling, multi-scale hierarchical analysis, H3 spatial graphs
- **Multi-Agent Coordination**: Utilities for coordinating multiple Active Inference agents

## Integration

- **Location**: `GEO-INFER-ACT/src/geo_infer_act/utils`
- **Type**: Utility Module Component
- **Dependencies**: NumPy, SciPy, Matplotlib for mathematical and visualization operations
- **Used By**: 
 
- `geo_infer_act.core` for mathematical utilities
 
- `geo_infer_act.models` for analysis and visualization
 
- `geo_infer_act.api` for integration utilities
