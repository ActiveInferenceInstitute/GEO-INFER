# Agent
: preprocessing 

## Scope
 This directory contains preprocessing components for the module. It provides 1 classes and 0 functions. 

## Classes
 and Functions 

### GeospatialFeatureEngineer
 Feature engineering for geospatial ML datasets.

**Methods**:
- `create_spatial_features(coordinates: np.ndarray, include_distances: bool, include_angles: bool) -> pd.DataFrame`: Create spatial features from coordinates.
- `create_temporal_features(timestamps: Union[np.ndarray, pd.Series, List]) -> pd.DataFrame`: Create temporal features from timestamps.
- `fit_transform(X: Union[np.ndarray, pd.DataFrame], coordinates: Optional[np.ndarray], timestamps: Optional[Union[np.ndarray, pd.Series, List]]) -> np.ndarray`: Fit the feature engineer and transform data.
- `transform(X: Union[np.ndarray, pd.DataFrame], coordinates: Optional[np.ndarray], timestamps: Optional[Union[np.ndarray, pd.Series, List]]) -> np.ndarray`: Transform data using fitted feature engineer.
- `get_feature_names() -> Optional[List[str]]`: Get feature names. 

## Capabilities
 
- **1 classes** for core functionality 

## Integration
 
- **Location**: `GEO-INFER-AI/src/geo_infer_ai/preprocessing` 
- **Type**: Directory Node
