# Agent
: predictive 

## Scope
 This directory contains predictive components for the module. It provides 1 classes and 0 functions. 

## Classes
 and Functions 

### SpatialPredictor
 Spatial predictor for geospatial regression and forecasting tasks.

**Methods**:
- `fit(X: Union[np.ndarray, pd.DataFrame], y: np.ndarray, sample_weight: Optional[np.ndarray], coordinates: Optional[np.ndarray]) -> 'SpatialPredictor'`: Train the spatial predictor.
- `predict(X: Union[np.ndarray, pd.DataFrame], coordinates: Optional[np.ndarray]) -> np.ndarray`: Make predictions.
- `get_feature_importance() -> Optional[np.ndarray]`: Get feature importance scores (for tree-based models).
- `get_feature_names() -> Optional[List[str]]`: Get feature names. 

## Capabilities
 
- **1 classes** for core functionality 

## Integration
 
- **Location**: `src/geo_infer_ai/models/predictive` 
- **Type**: Directory Node
