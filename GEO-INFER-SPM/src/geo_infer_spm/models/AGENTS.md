# Agent
: models

## Scope
 This directory contains models components for the module. It provides 4 classes and 0 functions.

## Classes
 and Functions

### SPMData
 Core data structure for SPM analysis containing geospatial observations.

**Methods**:
- `n_points() -> int`: Number of spatial/temporal points in the dataset.
- `has_temporal() -> bool`: Whether the data includes temporal information.
- `spatial_dims() -> Tuple[int, int]`: Spatial dimensions of the data.

### DesignMatrix
 Design matrix for General Linear Model specification.

**Methods**:
- `n_regressors() -> int`: Number of regressors in the design matrix.
- `n_points() -> int`: Number of data points.

### ContrastResult
 Results of a statistical contrast in SPM analysis.

**Methods**:
- `n_significant() -> int`: Number of significant points.

### SPMResult
 results from a Statistical Parametric Mapping analysis.

**Methods**:
- `r_squared() -> float`: Coefficient of determination for model fit.
- `log_likelihood() -> float`: Log-likelihood of the fitted model.
- `add_contrast(contrast: ContrastResult)`: Add a computed contrast to the results.
- `get_significant_clusters(contrast_idx: int) -> Optional[Dict[str, Any]]`: Get cluster analysis for a specific contrast.

## Capabilities

- **4 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-SPM/src/geo_infer_spm/models`
- **Type**: Directory Node
