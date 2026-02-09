# Agent
: models

## Scope
 This directory contains models components for the module. It provides 12 classes and 1 functions.

## Classes
 and Functions

### BayesianModel
 Abstract base class for all Bayesian models.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the model parameters.
- `log_posterior(theta: Dict[str, Any], data: Any) -> float`: Compute the log-posterior for the model.
- `prepare_data(data: Union[np.ndarray, xr.Dataset, Dict[str, Any]]) -> Any`: Prepare data for inference.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.
- `plot_prediction(posterior: Any, grid: Optional[np.ndarray], uncertainty: bool, **kwargs) -> Tuple[plt.Figure, plt.Axes]`: Plot model predictions from the posterior.

### BayesianNetwork
 Bayesian network model for geospatial causal inference.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the Bayesian network model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the Bayesian network model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### BayesianTimeSeriesModel
 Bayesian time series model for geospatial data.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the time series model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the time series model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### DirichletProcessMixture
 Dirichlet Process mixture model for spatial clustering.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the DP mixture model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the DP mixture model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### DynamicSpatialModel
 Dynamic spatial model for time-varying spatial processes.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the dynamic spatial model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the dynamic spatial model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### HierarchicalBayesianModel
 Hierarchical Bayesian model for multi-level spatial data.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the hierarchical model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the hierarchical model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### MultilevelModel
 Multi-level Bayesian model for complex hierarchical structures.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the multi-level model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the multi-level model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### SpatialCausalModel
 Spatial causal model for geospatial causal inference.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the spatial causal model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the spatial causal model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### SpatialClusteringModel
 Spatial clustering model for geospatial data.

**Methods**:
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the spatial clustering model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the spatial clustering model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### SpatialGP
 Gaussian Process model for spatial data.

**Methods**:
- `fit(X: np.ndarray, y: np.ndarray) -> 'SpatialGP'`: Fit the GP to training data.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.
- `log_likelihood(theta: Dict[str, Any], data: Dict[str, np.ndarray]) -> float`: Compute the marginal log-likelihood of the GP.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the GP parameters.

### SpatioTemporalConfig
 Configuration for spatio-temporal Gaussian Process models.

### SpatioTemporalGP
 Spatio-temporal Gaussian Process model for geospatial applications.

**Methods**:
- `fit(spatial_coords: np.ndarray, temporal_coords: np.ndarray, observations: np.ndarray, **kwargs) -> 'SpatioTemporalGP'`: Fit the spatio-temporal Gaussian Process model to data.
- `predict(spatial_coords: np.ndarray, temporal_coords: np.ndarray, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions using the fitted spatio-temporal model.
- `sample(spatial_coords: np.ndarray, temporal_coords: np.ndarray, n_samples: int) -> np.ndarray`: Generate samples from the spatio-temporal model.
- `get_model_parameters() -> Dict[str, Any]`: Get the fitted model parameters.
- `log_likelihood(spatial_coords: np.ndarray, temporal_coords: np.ndarray, observations: np.ndarray) -> float`: Calculate the log-likelihood of the data under the model.
- `cross_validate(spatial_coords: np.ndarray, temporal_coords: np.ndarray, observations: np.ndarray, n_folds: int) -> Dict[str, float]`: Perform cross-validation on the model.
- `log_likelihood(theta: Dict[str, Any], data: Any) -> float`: Compute the log-likelihood for the spatio-temporal model.
- `log_prior(theta: Dict[str, Any]) -> float`: Compute the log-prior for the spatio-temporal model parameters.
- `predict(X_new: np.ndarray, posterior: Any, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions at locations.
- `posterior_predictive(posterior: Any, X: Optional[np.ndarray], samples: int) -> np.ndarray`: Generate posterior predictive samples.

### create_spatiotemporal_gp
 `create_spatiotemporal_gp(config: Optional[SpatioTemporalConfig]) -> SpatioTemporalGP` Create a spatio-temporal Gaussian Process model.

## Capabilities

- **12 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-BAYES/src/geo_infer_bayes/models`
- **Type**: Directory Node
