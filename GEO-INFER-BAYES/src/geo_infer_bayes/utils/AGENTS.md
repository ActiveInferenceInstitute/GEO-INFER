# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 6 classes and 16 functions.

## Classes
 and Functions

### SpatialLikelihood
 Spatial likelihood functions for Bayesian models.

**Methods**:
- `log_likelihood(predictions: np.ndarray, observations: np.ndarray, spatial_weights: Optional[np.ndarray]) -> float`: Compute the log likelihood for spatial data.

### PoissonProcess
 Poisson process likelihood for spatial point patterns.

**Methods**:
- `log_likelihood(intensity: np.ndarray, points: np.ndarray, window: Dict[str, float]) -> float`: Compute the log likelihood for a spatial Poisson process.

### GaussianLikelihood
 Gaussian likelihood functions for Bayesian models.

**Methods**:
- `log_likelihood(predictions: np.ndarray, observations: np.ndarray) -> float`: Compute the Gaussian log likelihood.

### SpatialPrior
 Spatial prior distributions for Bayesian models.

**Methods**:
- `log_prior(spatial_field: np.ndarray, adjacency_matrix: np.ndarray) -> float`: Compute the log prior for a spatial field.

### TemporalPrior
 Temporal prior distributions for Bayesian models.

**Methods**:
- `log_prior(temporal_field: np.ndarray) -> float`: Compute the log prior for a temporal field.

### GaussianProcessPrior
 Gaussian Process prior distributions for Bayesian models.

**Methods**:
- `log_prior(lengthscale: float, variance: float) -> float`: Compute the log prior for GP hyperparameters.

### prepare_spatial_data
 `prepare_spatial_data(data: Union[pd.DataFrame, np.ndarray], lat_col: str, lon_col: str, value_col: Optional[str], time_col: Optional[str], **kwargs) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]` Prepare spatial data for Bayesian inference.

### load_geospatial_data
 `load_geospatial_data(file_path: Union[str, Path], file_format: Optional[str], **kwargs) -> pd.DataFrame` Load geospatial data from various file formats.

### validate_spatial_data
 `validate_spatial_data(spatial_coords: np.ndarray, values: np.ndarray, temporal_coords: Optional[np.ndarray]) -> Dict[str, Any]` Validate spatial data for Bayesian inference.

### create_spatial_grid
 `create_spatial_grid(bounds: Dict[str, float], resolution: float, grid_type: str) -> Tuple[np.ndarray, Dict[str, Any]]` Create a spatial grid for prediction.

### sample_spatial_data
 `sample_spatial_data(spatial_coords: np.ndarray, values: np.ndarray, n_samples: int, method: str, **kwargs) -> Tuple[np.ndarray, np.ndarray]` Sample spatial data for training/validation.

### save_processed_data
 `save_processed_data(data: pd.DataFrame, output_path: Union[str, Path], format: str, **kwargs)` Save processed data to file.

### mcmc_diagnostics
 `mcmc_diagnostics(samples: Dict[str, np.ndarray]) -> Dict[str, Any]` Compute MCMC diagnostics for posterior samples.

### convergence_metrics
 `convergence_metrics(samples: Dict[str, np.ndarray]) -> Dict[str, Any]` Compute convergence metrics for MCMC samples.

### plot_posterior
 `plot_posterior(samples: Dict[str, np.ndarray], parameters: Optional[List[str]]) -> plt.Figure` Plot posterior distributions for model parameters.

### plot_spatial_prediction
 `plot_spatial_prediction(spatial_coords: np.ndarray, predictions: np.ndarray, observations: Optional[np.ndarray], uncertainty: Optional[np.ndarray]) -> plt.Figure` Plot spatial predictions with optional uncertainty.

### plot_uncertainty
 `plot_uncertainty(predictions: np.ndarray, uncertainty: np.ndarray, confidence_level: float) -> plt.Figure` Plot prediction uncertainty with confidence intervals.

### plot_model_comparison
 `plot_model_comparison(models: List[str], metrics: Dict[str, List[float]]) -> plt.Figure` Plot comparison of different models.

## Capabilities

- **6 classes** for core functionality
- **16 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-BAYES/src/geo_infer_bayes/utils`
- **Type**: Directory Node
