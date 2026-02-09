# Agent
: models

## Scope
 This directory contains models components for the module. It provides 5 classes and 0 functions.

## Classes
 and Functions

### AgricultureModel
 Abstract base class for agricultural models.

**Methods**:
- `predict(data: Dict[str, Any]) -> Dict[str, Any]`: Generate predictions using the model.
- `validate_inputs(data: Dict[str, Any]) -> bool`: Validate that all required inputs are present.
- `info() -> Dict[str, Any]`: Get information about the model.
- `save(path: str) -> None`: Save the model to disk.
- `load(cls, path: str) -> 'AgricultureModel'`: Load a model from disk.

### CarbonSequestrationModel
 Model for predicting carbon sequestration in agricultural soils and biomass.

**Methods**:
- `fit(training_data: Dict[str, Any], target_columns: Optional[Dict[str, str]], feature_columns: Optional[List[str]]) -> None`: Train the carbon sequestration model using historical data.
- `predict(data: Dict[str, Any]) -> Dict[str, Any]`: Predict carbon sequestration potential using the model.
- `calculate_carbon_value(result: Dict[str, Any], carbon_price: float) -> Dict[str, Union[float, np.ndarray]]`: Calculate monetary value of carbon sequestration.
- `set_time_horizon(years: int) -> None`: Set the time horizon for carbon sequestration projections.
- `save(path: str) -> None`: Save the model to disk.
- `load(cls, path: str) -> 'CarbonSequestrationModel'`: Load a model from disk.

### CropYieldModel
 Model for predicting crop yields based on environmental and management factors.

**Methods**:
- `fit(training_data: Dict[str, Any], target_column: str, feature_columns: Optional[List[str]]) -> None`: Train the yield prediction model using historical data.
- `predict(data: Dict[str, Any]) -> Dict[str, Any]`: Predict crop yields using the model.
- `get_feature_importance() -> Dict[str, float]`: Get feature importance for machine learning models.
- `save(path: str) -> None`: Save the model to disk.
- `load(cls, path: str) -> 'CropYieldModel'`: Load a model from disk.

### SoilHealthModel
 Model for predicting and assessing soil health metrics.

**Methods**:
- `fit(training_data: Dict[str, Any], target_columns: Optional[Dict[str, str]], feature_columns: Optional[List[str]]) -> None`: Train the soil health prediction model using historical data.
- `predict(data: Dict[str, Any]) -> Dict[str, Any]`: Predict soil health indicators using the model.
- `get_limiting_factors(result: Dict[str, Any]) -> Dict[str, List[str]]`: Identify limiting soil health factors for each field.
- `save(path: str) -> None`: Save the model to disk.
- `load(cls, path: str) -> 'SoilHealthModel'`: Load a model from disk.

### WaterUsageModel
 Model for predicting agricultural water usage and requirements.

**Methods**:
- `fit(training_data: Dict[str, Any], target_column: str, feature_columns: Optional[List[str]]) -> None`: Train the water usage prediction model using historical data.
- `predict(data: Dict[str, Any]) -> Dict[str, Any]`: Predict water usage metrics using the model.
- `calculate_water_footprint(result: Dict[str, Any], yield_data: Optional[pd.Series]) -> Dict[str, Union[float, np.ndarray, pd.Series]]`: Calculate water footprint metrics from water usage results.
- `save(path: str) -> None`: Save the model to disk.
- `load(cls, path: str) -> 'WaterUsageModel'`: Load a model from disk.

## Capabilities

- **5 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-AG/src/geo_infer_ag/models`
- **Type**: Directory Node
