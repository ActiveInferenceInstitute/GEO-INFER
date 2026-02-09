# Agent
: api

## Scope
 This directory contains api components for the module. It provides 3 classes and 0 functions.

## Classes
 and Functions

### PyMCInterface
 Interface to PyMC for Bayesian computation.

**Methods**:
- `create_spatial_gp_model(X: np.ndarray, y: np.ndarray, kernel_type: str, **kwargs) -> pm.Model`: Create a PyMC Gaussian Process model for spatial data.
- `create_hierarchical_model(X: np.ndarray, y: np.ndarray, groups: np.ndarray, **kwargs) -> pm.Model`: Create a PyMC hierarchical Bayesian model.
- `sample(n_samples: int, n_warmup: int, chains: int, cores: int, sampler: str, **kwargs) -> az.InferenceData`: Sample from the PyMC model.
- `predict(X_new: np.ndarray, samples: int, return_std: bool) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]`: Make predictions using the PyMC model.
- `convert_to_geo_infer_format(trace: Optional[az.InferenceData]) -> Dict[str, np.ndarray]`: Convert PyMC trace to GEO-INFER-BAYES format.

### StanInterface
 Interface to Stan for Bayesian computation.

**Methods**:
- `create_spatial_gp_model(X: np.ndarray, y: np.ndarray, **kwargs) -> str`: Create a Stan model for spatial Gaussian Process.
- `sample(n_samples: int, n_warmup: int, **kwargs) -> Dict[str, np.ndarray]`: Sample from the Stan model.

### TFPInterface
 Interface to TensorFlow Probability for Bayesian computation.

**Methods**:
- `create_spatial_gp_model(X: np.ndarray, y: np.ndarray, **kwargs) -> str`: Create a TensorFlow Probability model for spatial Gaussian Process.
- `sample(n_samples: int, n_warmup: int, **kwargs) -> Dict[str, np.ndarray]`: Sample from the TensorFlow Probability model.

## Capabilities

- **3 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-BAYES/src/geo_infer_bayes/api`
- **Type**: Directory Node
