# Agent
: core ## Scope
 This directory contains core components for the module. It provides 6 classes and 12 functions. ## Classes
 and Functions ### BayesianSP
M
 Bayesian Statistical Parametric Mapping implementation. **Methods**: - `fit_bayesian_glm(data: SPMData, design_matrix: np.ndarray, priors: Optional[Dict[str, Any]], n_samples: int, n_tune: int) -> SPMResult`: Fit Bayesian GLM using MCMC sampling. - `posterior_probability_map(statistical_map: np.ndarray, threshold: float) -> np.ndarray`: Compute posterior probability map. - `bayesian_model_comparison(models: List[SPMResult], method: str) -> Dict[str, Any]`: Compare Bayesian models using Bayes factors or information criteria. - `spatial_hierarchical_model(data: SPMData, design_matrix: np.ndarray, spatial_structure: Dict[str, Any]) -> SPMResult`: Fit spatial hierarchical Bayesian model. - `variational_inference(data: SPMData, design_matrix: np.ndarray, n_iterations: int) -> SPMResult`: Perform variational inference for scalable Bayesian computation. ### Contras
t
 Contrast specification for SPM hypothesis testing. **Methods**: - `from_string(cls, contrast_str: str, design_names: List[str], contrast_type: str) -> 'Contrast'`: Create contrast from string specification. ### GeneralLinearMode
l
 General Linear Model for geospatial SPM analysis. **Methods**: - `fit(data: SPMData, method: str, spatial_regularization: Optional[Dict[str, Any]]) -> SPMResult`: Fit the GLM to geospatial data. - `predict(new_data: Optional[SPMData], new_design: Optional[np.ndarray]) -> np.ndarray`: Make predictions using the fitted GLM. - `get_coefficient_test(coefficient_idx: int) -> Dict[str, Any]`: Test significance of a specific coefficient. ### RandomFieldTheor
y
 Random Field Theory for multiple comparison correction in SPM. **Methods**: - `estimate_smoothness(residuals: np.ndarray, mask: Optional[np.ndarray]) -> np.ndarray`: Estimate field smoothness using residuals. - `compute_search_volume(voxel_sizes: Optional[np.ndarray]) -> float`: Compute search volume in resels (resolution elements). - `expected_clusters(threshold: float, stat_type: str) -> float`: Compute expected number of clusters above threshold. - `cluster_threshold(alpha: float, stat_type: str) -> float`: Compute cluster-forming threshold for given alpha level. - `peak_threshold(alpha: float, stat_type: str) -> float`: Compute peak-level threshold for given alpha level. - `correct_p_values(statistical_map: np.ndarray, stat_type: str, method: str) -> np.ndarray`: Apply RFT-based multiple comparison correction. ### SpatialAnalyze
r
 Spatial analysis tools for SPM data. **Methods**: - `estimate_variogram(residuals: np.ndarray, n_bins: int, max_distance: Optional[float]) -> Dict[str, Any]`: Estimate empirical variogram from residuals. - `create_spatial_weights(model_type: str, **kwargs) -> np.ndarray`: Create spatial weights matrix based on fitted variogram. - `detect_clusters(statistical_map: np.ndarray, threshold: float, min_cluster_size: int) -> Dict[str, Any]`: Detect significant clusters in statistical parametric map. - `geographically_weighted_regression(data: SPMData, bandwidth: float) -> SPMResult`: Perform geographically weighted regression (GWR). - `spatial_basis_functions(n_basis: int, basis_type: str) -> np.ndarray`: Generate spatial basis functions for modeling spatial variation. ### TemporalAnalyze
r
 Temporal analysis tools for SPM data. **Methods**: - `detect_trends(data: np.ndarray, method: str, alpha: float) -> Dict[str, Any]`: Detect temporal trends in SPM data. - `seasonal_decomposition(data: np.ndarray, period: Optional[int], model: str) -> Dict[str, Any]`: Decompose time series into trend, seasonal, and residual components. - `fit_arima_model(data: np.ndarray, order: Tuple[int, int, int], seasonal_order: Optional[Tuple[int, int, int, int]]) -> Dict[str, Any]`: Fit ARIMA model to time series data. - `sliding_window_analysis(data: np.ndarray, window_size: int, step_size: int, analysis_func: Optional[callable]) -> Dict[str, Any]`: Perform sliding window analysis for dynamic temporal patterns. - `change_point_detection(data: np.ndarray, method: str, penalty: float) -> Dict[str, Any]`: Detect change points in time series data. - `temporal_basis_functions(n_basis: int, basis_type: str) -> np.ndarray`: Generate temporal basis functions for modeling temporal variation. ### negative_log_posterio
r
 `negative_log_posterior(beta)` Negative log posterior for optimization. ### contras
t
 `contrast(model_result: SPMResult, contrast_spec: Union[str, np.ndarray, Contrast], contrast_type: str) -> ContrastResult` Define and compute a contrast for SPM analysis. ### generate_common_contrast
s
 `generate_common_contrasts(design_matrix: 'DesignMatrix', design_type: str) -> List[Contrast]` Generate common contrasts for standard experimental designs. ### fit_gl
m
 `fit_glm(data: SPMData, design_matrix: DesignMatrix, method: str, **kwargs) -> SPMResult` Convenience function to fit a GLM to geospatial data. ### compute_sp
m
 `compute_spm(model_result: SPMResult, contrast: ContrastResult, correction: str, alpha: float) -> ContrastResult` Compute Statistical Parametric Map with multiple comparison correction. ### expected_clusters_fun
c
 `expected_clusters_func(u)` ### spherical_mode
l
 `spherical_model(h, nugget, sill, range_)` Spherical variogram model. ### exponential_mode
l
 `exponential_model(h, nugget, sill, range_)` Exponential variogram model. ### gaussian_mode
l
 `gaussian_model(h, nugget, sill, range_)` Gaussian variogram model. ### objectiv
e
 `objective(params)` ## Capabilities
 - **6 classes** for core functionality - **12 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SPM/src/geo_infer_spm/core` - **Type**: Directory Node 