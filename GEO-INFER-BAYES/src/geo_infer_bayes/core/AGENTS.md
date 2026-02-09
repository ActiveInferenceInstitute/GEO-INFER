# Agent
: core

## Scope
 This directory contains core components for the module. It provides 8 classes and 0 functions.

## Classes
 and Functions

### ApproximateBayesianComputation
 Approximate Bayesian Computation (ABC) for Bayesian inference.

**Methods**:
- `run(observed_data: Any, simulator: Optional[Callable], progress_bar: bool, **kwargs) -> Union[Dict[str, np.ndarray], Any]`: Run ABC sampling for the model.
- `update(new_data: Any, previous_samples: Union[Dict[str, np.ndarray], Any], **kwargs) -> Union[Dict[str, np.ndarray], Any]`: Update ABC samples with data.

### HMC
 Hamiltonian Monte Carlo (HMC) for Bayesian inference.

**Methods**:
- `run(data: Any, n_samples: int, n_warmup: int, thin: int, init_strategy: str, use_nuts: bool, progress_bar: bool, **kwargs) -> Union[Dict[str, np.ndarray], xr.Dataset]`: Run HMC sampling for the model.
- `update(new_data: Any, previous_samples: Union[Dict[str, np.ndarray], xr.Dataset], n_samples: int, **kwargs) -> Union[Dict[str, np.ndarray], xr.Dataset]`: Update previous samples with data.

### BayesianInference
 Main class for performing Bayesian inference on geospatial data.

**Methods**:
- `run(data: Union[np.ndarray, xr.Dataset, Dict[str, Any]], **kwargs) -> PosteriorAnalysis`: Run the inference algorithm on the provided data.
- `update(new_data: Union[np.ndarray, xr.Dataset, Dict[str, Any]], previous_posterior: PosteriorAnalysis, **kwargs) -> PosteriorAnalysis`: Update a previous posterior with data (sequential inference).

### MCMC
 Markov Chain Monte Carlo (MCMC) for Bayesian inference.

**Methods**:
- `run(data: Any, n_samples: int, n_warmup: int, thin: int, init_strategy: str, progress_bar: bool, **kwargs) -> Union[Dict[str, np.ndarray], xr.Dataset]`: Run MCMC sampling for the model.
- `update(new_data: Any, previous_samples: Union[Dict[str, np.ndarray], xr.Dataset], n_samples: int, **kwargs) -> Union[Dict[str, np.ndarray], xr.Dataset]`: Update previous samples with data.

### ModelComparison
 Tools for comparing and selecting Bayesian models.

**Methods**:
- `compare_models(data: Any, method: str) -> Dict[str, Any]`: Compare models using specified method.
- `get_best_model(criterion: str) -> Any`: Get the best model according to the specified criterion.
- `plot_comparison() -> None`: Plot model comparison results.

### PosteriorAnalysis
 Analyze and visualize posterior distributions from Bayesian inference.

**Methods**:
- `summary(parameters: Optional[List[str]]) -> pd.DataFrame`: Summarize the posterior distribution.
- `plot_trace(parameters: Optional[List[str]]) -> None`: Plot MCMC traces for the posterior samples.
- `plot_posterior(parameters: Optional[List[str]]) -> None`: Plot posterior distributions.
- `plot_forest(parameters: Optional[List[str]]) -> None`: Forest plot of posterior distributions.
- `plot_spatial_prediction(grid: Optional[np.ndarray], uncertainty: bool) -> Tuple[plt.Figure, plt.Axes]`: Plot spatial predictions from the posterior.
- `predict(X_new: np.ndarray, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations using the posterior.
- `credible_interval(parameter: str, alpha: float) -> Tuple[float, float]`: Compute credible interval for a parameter.
- `posterior_predictive(X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### SequentialMonteCarlo
 Sequential Monte Carlo (SMC) for Bayesian inference.

**Methods**:
- `run(data: Any, n_steps: int, progress_bar: bool, **kwargs) -> Union[Dict[str, np.ndarray], Any]`: Run SMC sampling for the model.
- `update(new_data: Any, previous_samples: Union[Dict[str, np.ndarray], Any], **kwargs) -> Union[Dict[str, np.ndarray], Any]`: Update particles with data.

### VariationalInference
 Variational Inference (VI) for scalable Bayesian approximation.

**Methods**:
- `run(data: Any, progress_bar: bool, **kwargs) -> Union[Dict[str, np.ndarray], xr.Dataset]`: Run variational inference for the model.
- `update(new_data: Any, previous_samples: Union[Dict[str, np.ndarray], xr.Dataset], **kwargs) -> Union[Dict[str, np.ndarray], xr.Dataset]`: Update the approximate posterior with data.

## Capabilities

- **8 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-BAYES/src/geo_infer_bayes/core`
- **Type**: Directory Node
