# Agent
: models

## Scope
 This directory contains models components for the module. It provides 12 classes and 8 functions.

## Classes
 and Functions

### ClusteringResults
 Container for clustering analysis results.

### SpatialKMeans
 Spatially constrained K-means clustering.

**Methods**:
- `fit(X: np.ndarray, coordinates: Optional[np.ndarray]) -> 'SpatialKMeans'`: Fit K-means clustering.
- `predict(X: np.ndarray) -> np.ndarray`: Predict cluster labels for data.
- `fit_predict(X: np.ndarray, coordinates: Optional[np.ndarray]) -> np.ndarray`: Fit model and return cluster labels.

### SpatiallyConstrainedKMeans
 Spatially constrained K-means clustering.

**Methods**:
- `fit(X: np.ndarray, coordinates: np.ndarray) -> 'SpatiallyConstrainedKMeans'`: Fit spatially constrained K-means.
- `predict(X: np.ndarray, coordinates: np.ndarray) -> np.ndarray`: Predict cluster labels.

### SpatialDBSCAN
 Density-based spatial clustering of applications with noise (DBSCAN).

**Methods**:
- `fit(X: np.ndarray, coordinates: Optional[np.ndarray]) -> 'SpatialDBSCAN'`: Fit DBSCAN clustering.
- `fit_predict(X: np.ndarray, coordinates: Optional[np.ndarray]) -> np.ndarray`: Fit model and return cluster labels.

### SKATERClustering
 Spatial 'K'luster Analysis by Tree Edge Removal (SKATER) clustering.

**Methods**:
- `fit(X: np.ndarray, coordinates: np.ndarray) -> 'SKATERClustering'`: Fit SKATER clustering.

### HierarchicalClustering
 Hierarchical clustering with spatial constraints.

**Methods**:
- `fit(X: np.ndarray, coordinates: Optional[np.ndarray]) -> 'HierarchicalClustering'`: Fit hierarchical clustering.
- `fit_predict(X: np.ndarray, coordinates: Optional[np.ndarray]) -> np.ndarray`: Fit model and return cluster labels.

### RegressionResults
 Container for regression analysis results.

### OrdinaryLeastSquares
 Ordinary Least Squares regression.

**Methods**:
- `fit(X: np.ndarray, y: np.ndarray) -> 'OrdinaryLeastSquares'`: Fit OLS regression model.
- `predict(X: np.ndarray) -> np.ndarray`: Make predictions using fitted model.
- `score(X: np.ndarray, y: np.ndarray) -> float`: Calculate R-squared score.

### SpatialLagModel
 Spatial Lag (SAR) regression model.

**Methods**:
- `fit(X: np.ndarray, y: np.ndarray) -> 'SpatialLagModel'`: Fit spatial lag model.
- `predict(X: np.ndarray) -> np.ndarray`: Make predictions.

### GeographicallyWeightedRegression
 Geographically Weighted Regression (GWR).

**Methods**:
- `fit(X: np.ndarray, y: np.ndarray, coordinates: np.ndarray) -> 'GeographicallyWeightedRegression'`: Fit GWR model.
- `predict(X: np.ndarray, coordinates: np.ndarray) -> np.ndarray`: Make predictions at given coordinates.

### SpatialErrorModel
 Spatial Error Model (SEM).

**Methods**:
- `fit(X: np.ndarray, y: np.ndarray) -> 'SpatialErrorModel'`: Fit spatial error model.
- `predict(X: np.ndarray) -> np.ndarray`: Make predictions.

### SpatialDurbinModel
 Spatial Durbin Model (SDM).

**Methods**:
- `fit(X: np.ndarray, y: np.ndarray) -> 'SpatialDurbinModel'`: Fit spatial Durbin model.
- `predict(X: np.ndarray) -> np.ndarray`: Make predictions.

### spatial_clustering_analysis
 `spatial_clustering_analysis(X: np.ndarray, coordinates: np.ndarray, method: str, **kwargs) -> ClusteringResults` Perform spatial clustering analysis.

### find
 `find(x)`

### union
 `union(x, y)`

### spatial_regression_analysis
 `spatial_regression_analysis(X: np.ndarray, y: np.ndarray, coordinates: np.ndarray, model_type: str) -> Dict[str, Any]` Perform spatial regression analysis.

### log_likelihood
 `log_likelihood(params)`

### cv_score
 `cv_score(bandwidth)`

### log_likelihood
 `log_likelihood(params)`

### log_likelihood
 `log_likelihood(params)`

## Capabilities

- **12 classes** for core functionality
- **8 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-MATH/src/geo_infer_math/models`
- **Type**: Directory Node
