# Agent
: core ## Scope
 This directory contains core components for the module. It provides 10 classes and 2 functions. ## Classes
 and Functions ### SpatialWeightsConfi
g
 Configuration for spatial weights matrix construction. ### EconometricResult
s
 Container for econometric estimation results. ### SpatialEconometricsEngin
e
 spatial econometric analysis engine. **Methods**: - `construct_spatial_weights(gdf: gpd.GeoDataFrame, config: SpatialWeightsConfig) -> np.ndarray`: Construct spatial weights matrix from geographic data. - `fit(X: np.ndarray, y: np.ndarray, W: Optional[np.ndarray], model_type: str) -> 'SpatialEconometricsEngine'`: Fit spatial econometric model (sklearn-compatible interface). - `predict(X: np.ndarray, W: Optional[np.ndarray]) -> np.ndarray`: Make predictions using fitted spatial model (sklearn-compatible). - `score(X: np.ndarray, y: np.ndarray, sample_weight: Optional[np.ndarray]) -> float`: Return the coefficient of determination R^2 of the prediction (sklearn-compatible). - `get_params(deep: bool) -> Dict[str, Any]`: Get parameters for this estimator (sklearn-compatible). - `set_params(**params) -> 'SpatialEconometricsEngine'`: Set parameters for this estimator (sklearn-compatible). - `geographically_weighted_regression(y: np.ndarray, X: np.ndarray, coordinates: np.ndarray, bandwidth: Optional[float]) -> Dict[str, np.ndarray]`: Perform Geographically Weighted Regression (GWR). - `spatial_diagnostics(residuals: np.ndarray, W: np.ndarray) -> Dict[str, float]`: spatial diagnostic tests. - `cross_validate_spatial_model(X: np.ndarray, y: np.ndarray, W: np.ndarray, cv_folds: int, model_type: str) -> Dict[str, Any]`: Perform cross-validation for spatial models. ### ModelConfiguratio
n
 Configuration settings for economic models. ### EconomicModelingEngin
e
 Core engine for orchestrating and executing economic models. **Methods**: - `register_model(model_name: str, model_class: type) -> None`: Register a model class for use by the engine. - `create_model(model_name: str, model_config: ModelConfiguration) -> Any`: Create and initialize a model instance. - `execute_model(model_instance: Any, data: Dict[str, Any]) -> Dict[str, Any]`: Execute a model with provided data. - `batch_execute(models: List[tuple], common_data: Dict[str, Any]) -> Dict[str, Any]`: Execute multiple models with common data. - `get_model_info(model_name: str) -> Dict[str, Any]`: Get information about a registered model. - `list_models() -> List[str]`: List all registered models. - `cleanup() -> None`: Clean up resources and active model instances. ### PolicyTyp
e
 Types of economic policies. ### PolicyScenari
o
 Definition of a policy scenario for analysis. ### PolicyImpac
t
 Container for policy impact results. ### PolicyCompariso
n
 Comparison of multiple policy scenarios. ### PolicyAnalysisEngin
e
 framework for economic policy impact assessment. **Methods**: - `add_baseline_data(data_type: str, data: Union[pd.DataFrame, Dict[str, Any]]) -> None`: Add baseline economic data for policy analysis. - `define_scenario(scenario: PolicyScenario) -> None`: Define a policy scenario for analysis. - `assess_fiscal_policy(scenario: PolicyScenario) -> PolicyImpact`: Assess the impact of fiscal policy changes. - `assess_infrastructure_policy(scenario: PolicyScenario) -> PolicyImpact`: Assess the impact of infrastructure investment policies. - `assess_environmental_policy(scenario: PolicyScenario) -> PolicyImpact`: Assess the impact of environmental policies. - `compare_scenarios(scenario_names: List[str], weights: Optional[Dict[str, float]]) -> PolicyComparison`: Compare multiple policy scenarios. ### sar_log_likelihoo
d
 `sar_log_likelihood(params)` SAR model log-likelihood function. ### sem_log_likelihoo
d
 `sem_log_likelihood(params)` SEM model log-likelihood function. ## Capabilities
 - **10 classes** for core functionality - **2 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-ECON/src/geo_infer_econ/core` - **Type**: Directory Node 