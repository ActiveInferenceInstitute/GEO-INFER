# Agent
: convenience ## Scope
 This directory contains convenience components for the module. It provides 6 classes and 15 functions. ## Classes
 and Functions ### ActiveInferenceConvenienc
e
 Convenience class for Active Inference operations. **Methods**: - `calculate_free_energy(observations: np.ndarray, beliefs: np.ndarray, **kwargs) -> float`: Calculate free energy. - `variational_inference(observations: np.ndarray, prior: np.ndarray, **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]`: Perform variational inference. - `update_beliefs(current_beliefs: np.ndarray, new_observations: np.ndarray) -> np.ndarray`: Update beliefs with observations. ### AIConvenienc
e
 Convenience class for AI/ML operations. **Methods**: - `compute_gradient(function: Callable, parameters: np.ndarray, **kwargs) -> np.ndarray`: Compute gradient. - `calculate_loss(predictions: np.ndarray, targets: np.ndarray, **kwargs) -> float`: Calculate loss. - `optimize(objective: Callable, initial_guess: np.ndarray, **kwargs) -> Tuple[np.ndarray, float, Dict[str, Any]]`: Optimize objective function. ### BayesianConvenienc
e
 Convenience class for Bayesian inference operations. **Methods**: - `calculate_posterior(prior: np.ndarray, likelihood: Callable, data: np.ndarray, **kwargs) -> np.ndarray`: Calculate posterior distribution. - `build_prior(distribution_type: str, **kwargs) -> np.ndarray`: Build prior distribution. - `mcmc_sample(log_posterior: Callable, initial_state: np.ndarray, **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]`: Perform MCMC sampling. - `optimize(objective: Callable, prior: np.ndarray, **kwargs) -> Tuple[np.ndarray, float, Dict[str, Any]]`: Perform Bayesian optimization. ### InformationTheoryConvenienc
e
 Convenience class for information theory operations. **Methods**: - `calculate_entropy(data: np.ndarray, method: str, **kwargs) -> float`: Calculate entropy. - `calculate_mutual_information(probabilities_xy: np.ndarray, probabilities_x: np.ndarray, probabilities_y: np.ndarray, **kwargs) -> float`: Calculate mutual information. - `calculate_kl_divergence(p: np.ndarray, q: np.ndarray, **kwargs) -> float`: Calculate KL divergence. ### IntegrationConvenienc
e
 Convenience class for cross-module integration. **Methods**: - `execute_cross_module(module_name: str, operation: str, data: Dict[str, Any], **kwargs) -> Any`: Execute cross-module operation. ### SpatialConvenienc
e
 Convenience class for spatial analysis. **Methods**: - `comprehensive_analysis(coordinates: np.ndarray, values: np.ndarray, **kwargs) -> Dict[str, Any]`: Perform spatial analysis. ### free_energy_calculatio
n
 `free_energy_calculation(observations: np.ndarray, beliefs: np.ndarray, generative_model: Optional[Callable], precision: float) -> float` Calculate variational free energy for Active Inference. ### variational_inference_helpe
r
 `variational_inference_helper(observations: np.ndarray, prior: np.ndarray, likelihood: Optional[Callable], max_iterations: int, tolerance: float) -> Tuple[np.ndarray, Dict[str, Any]]` Helper for variational inference in Active Inference. ### belief_updating_helpe
r
 `belief_updating_helper(current_beliefs: np.ndarray, new_observations: np.ndarray, precision: float) -> np.ndarray` Helper for belief updating in Active Inference. ### gradient_helpe
r
 `gradient_helper(function: Callable, parameters: np.ndarray, method: str, epsilon: float) -> np.ndarray` Helper for computing gradients. ### spatial_loss_functio
n
 `spatial_loss_function(predictions: np.ndarray, targets: np.ndarray, coordinates: Optional[np.ndarray], loss_type: str, spatial_weight: float) -> float` Spatial loss function for neural networks. ### optimization_wrappe
r
 `optimization_wrapper(objective: Callable, initial_guess: np.ndarray, method: str, **kwargs) -> Tuple[np.ndarray, float, Dict[str, Any]]` Wrapper for optimization algorithms. ### posterior_helpe
r
 `posterior_helper(prior: np.ndarray, likelihood: Callable, data: np.ndarray, normalize: bool) -> np.ndarray` Helper for calculating posterior distribution. ### prior_builde
r
 `prior_builder(distribution_type: str, parameters: Optional[Dict[str, Any]], size: int) -> np.ndarray` Build prior distribution. ### mcmc_wrappe
r
 `mcmc_wrapper(log_posterior: Callable, initial_state: np.ndarray, n_samples: int, n_burnin: int, step_size: float, method: str) -> Tuple[np.ndarray, Dict[str, Any]]` Wrapper for MCMC sampling. ### bayesian_optimization_helpe
r
 `bayesian_optimization_helper(objective: Callable, prior: np.ndarray, n_iterations: int, acquisition: str) -> Tuple[np.ndarray, float, Dict[str, Any]]` Helper for Bayesian optimization. ### spatial_entropy_helpe
r
 `spatial_entropy_helper(coordinates: np.ndarray, values: Optional[np.ndarray], method: str, **kwargs) -> float` Helper for calculating spatial entropy. ### mutual_information_helpe
r
 `mutual_information_helper(coordinates_x: np.ndarray, values_x: np.ndarray, coordinates_y: np.ndarray, values_y: np.ndarray, **kwargs) -> float` Helper for calculating spatial mutual information. ### kl_divergence_helpe
r
 `kl_divergence_helper(coordinates_p: np.ndarray, values_p: np.ndarray, coordinates_q: np.ndarray, values_q: np.ndarray, **kwargs) -> float` Helper for calculating spatial KL divergence. ### cross_module_helpe
r
 `cross_module_helper(module_name: str, operation: str, data: Dict[str, Any], **kwargs) -> Any` Helper for cross-module operations. ### enhanced_spatial_analysi
s
 `enhanced_spatial_analysis(coordinates: np.ndarray, values: np.ndarray, analysis_types: Optional[List[str]]) -> Dict[str, Any]` Spatial analysis combining multiple methods. ## Capabilities
 - **6 classes** for core functionality - **15 functions** for utility operations ## Integration
 - **Location**: `src/geo_infer_math/api/convenience` - **Type**: Directory Node 