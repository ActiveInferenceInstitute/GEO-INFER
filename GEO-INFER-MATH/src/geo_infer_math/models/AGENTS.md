# Agent
: models ## Scope
 This directory contains models components for the module. It provides 12 classes and 8 functions. ## Classes
 and Functions ### ClusteringResult
s
 Container for clustering analysis results. ### SpatialKMean
s
 Spatially constrained K-means clustering. **Methods**: - `fit(X: np.ndarray, coordinates: Optional[np.ndarray]) -> 'SpatialKMeans'`: Fit K-means clustering. - `predict(X: np.ndarray) -> np.ndarray`: Predict cluster labels for data. - `fit_predict(X: np.ndarray, coordinates: Optional[np.ndarray]) -> np.ndarray`: Fit model and return cluster labels. ### SpatiallyConstrainedKMean
s
 Spatially constrained K-means clustering. **Methods**: - `fit(X: np.ndarray, coordinates: np.ndarray) -> 'SpatiallyConstrainedKMeans'`: Fit spatially constrained K-means. - `predict(X: np.ndarray, coordinates: np.ndarray) -> np.ndarray`: Predict cluster labels. ### SpatialDBSCA
N
 Density-based spatial clustering of applications with noise (DBSCAN). **Methods**: - `fit(X: np.ndarray, coordinates: Optional[np.ndarray]) -> 'SpatialDBSCAN'`: Fit DBSCAN clustering. - `fit_predict(X: np.ndarray, coordinates: Optional[np.ndarray]) -> np.ndarray`: Fit model and return cluster labels. ### SKATERClusterin
g
 Spatial 'K'luster Analysis by Tree Edge Removal (SKATER) clustering. **Methods**: - `fit(X: np.ndarray, coordinates: np.ndarray) -> 'SKATERClustering'`: Fit SKATER clustering. ### HierarchicalClusterin
g
 Hierarchical clustering with spatial constraints. **Methods**: - `fit(X: np.ndarray, coordinates: Optional[np.ndarray]) -> 'HierarchicalClustering'`: Fit hierarchical clustering. - `fit_predict(X: np.ndarray, coordinates: Optional[np.ndarray]) -> np.ndarray`: Fit model and return cluster labels. ### RegressionResult
s
 Container for regression analysis results. ### OrdinaryLeastSquare
s
 Ordinary Least Squares regression. **Methods**: - `fit(X: np.ndarray, y: np.ndarray) -> 'OrdinaryLeastSquares'`: Fit OLS regression model. - `predict(X: np.ndarray) -> np.ndarray`: Make predictions using fitted model. - `score(X: np.ndarray, y: np.ndarray) -> float`: Calculate R-squared score. ### SpatialLagMode
l
 Spatial Lag (SAR) regression model. **Methods**: - `fit(X: np.ndarray, y: np.ndarray) -> 'SpatialLagModel'`: Fit spatial lag model. - `predict(X: np.ndarray) -> np.ndarray`: Make predictions. ### GeographicallyWeightedRegressio
n
 Geographically Weighted Regression (GWR). **Methods**: - `fit(X: np.ndarray, y: np.ndarray, coordinates: np.ndarray) -> 'GeographicallyWeightedRegression'`: Fit GWR model. - `predict(X: np.ndarray, coordinates: np.ndarray) -> np.ndarray`: Make predictions at given coordinates. ### SpatialErrorMode
l
 Spatial Error Model (SEM). **Methods**: - `fit(X: np.ndarray, y: np.ndarray) -> 'SpatialErrorModel'`: Fit spatial error model. - `predict(X: np.ndarray) -> np.ndarray`: Make predictions. ### SpatialDurbinMode
l
 Spatial Durbin Model (SDM). **Methods**: - `fit(X: np.ndarray, y: np.ndarray) -> 'SpatialDurbinModel'`: Fit spatial Durbin model. - `predict(X: np.ndarray) -> np.ndarray`: Make predictions. ### spatial_clustering_analysi
s
 `spatial_clustering_analysis(X: np.ndarray, coordinates: np.ndarray, method: str, **kwargs) -> ClusteringResults` Perform spatial clustering analysis. ### fin
d
 `find(x)` ### unio
n
 `union(x, y)` ### spatial_regression_analysi
s
 `spatial_regression_analysis(X: np.ndarray, y: np.ndarray, coordinates: np.ndarray, model_type: str) -> Dict[str, Any]` Perform spatial regression analysis. ### log_likelihoo
d
 `log_likelihood(params)` ### cv_scor
e
 `cv_score(bandwidth)` ### log_likelihoo
d
 `log_likelihood(params)` ### log_likelihoo
d
 `log_likelihood(params)` ## Capabilities
 - **12 classes** for core functionality - **8 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-MATH/src/geo_infer_math/models` - **Type**: Directory Node 