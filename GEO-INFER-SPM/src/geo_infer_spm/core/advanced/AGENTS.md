# Agent
: ## Scope
 This directory contains components for the module. It provides 4 classes and 8 functions. ## Classes
 and Functions ### MixedEffectsSP
M
 Mixed Effects Statistical Parametric Mapping **Methods**: - `fit(data: SPMData, method: str, optimizer: str) -> SPMResult`: Fit mixed effects model to SPM data. - `predict(new_data: SPMData, include_random_effects: bool) -> np.ndarray`: Make predictions using fitted mixed effects model. - `get_random_effects() -> Dict[str, np.ndarray]`: Extract estimated random effects. - `anova(other_model: 'MixedEffectsSPM') -> Dict[str, Any]`: Perform likelihood ratio test comparing two nested models. ### ModelValidato
r
 model validation for SPM analysis. **Methods**: - `cross_validate(model_func, data: SPMData, design_matrix, **model_kwargs) -> Dict[str, Any]`: Perform cross-validation of SPM model. - `compare_models(model_results: List[SPMResult], method: str) -> Dict[str, Any]`: Compare multiple fitted models. - `diagnostic_tests(model_result: SPMResult) -> Dict[str, Any]`: Perform diagnostic tests on fitted model. ### NonparametricSP
M
 Nonparametric Statistical Parametric Mapping **Methods**: - `fit(data: SPMData, design_matrix: DesignMatrix, response_var: Optional[str]) -> SPMResult`: Fit nonparametric model to SPM data. - `predict(new_data: SPMData) -> np.ndarray`: Make predictions using fitted nonparametric model. - `get_smooth_components() -> Optional[np.ndarray]`: Get smooth function components (for GAM). ### SpatialRegressio
n
 Spatial regression models for SPM analysis. **Methods**: - `fit(data: SPMData, design_matrix: DesignMatrix, **kwargs) -> SPMResult`: Fit spatial regression model. - `predict(new_data: SPMData) -> np.ndarray`: Make spatial predictions. - `get_spatial_effects() -> Dict[str, Any]`: Extract spatial effects from fitted model. ### fit_mixed_effect
s
 `fit_mixed_effects(data: SPMData, fixed_design: DesignMatrix, random_groups: Dict[str, np.ndarray], **kwargs) -> SPMResult` Convenience function to fit mixed effects SPM model. ### negative_reml_logli
k
 `negative_reml_loglik(params)` Negative REML log-likelihood. ### negative_ml_logli
k
 `negative_ml_loglik(params)` ### validate_spm_mode
l
 `validate_spm_model(model_result: SPMResult, validation_data: Optional[SPMData], method: str) -> Dict[str, Any]` Convenience function for SPM model validation. ### fit_nonparametri
c
 `fit_nonparametric(data: SPMData, design_matrix: DesignMatrix, method: str, **kwargs) -> SPMResult` Convenience function to fit nonparametric SPM model. ### fit_spatial_mode
l
 `fit_spatial_model(data: SPMData, design_matrix: DesignMatrix, model_type: str, **kwargs) -> SPMResult` Convenience function to fit spatial regression model. ### sar_logli
k
 `sar_loglik(params)` ### sem_logli
k
 `sem_loglik(params)` ## Capabilities
 - **4 classes** for core functionality - **8 functions** for utility operations ## Integration
 - **Location**: `src/geo_infer_spm/core/advanced` - **Type**: Directory Node 