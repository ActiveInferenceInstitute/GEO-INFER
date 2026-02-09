# Agent
: core

## Scope
 This directory contains core components for the module. It provides 4 classes and 0 functions.

## Classes
 and Functions

### ModelExplainer
 Explain geospatial AI model predictions.

**Methods**:
- `calculate_feature_importance(X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]], method: str) -> Dict[str, float]`: Calculate feature importance.
- `explain_prediction(X: np.ndarray, prediction: float, feature_names: Optional[List[str]]) -> Dict[str, Any]`: Explain a single prediction.
- `generate_spatial_explanation(spatial_features: np.ndarray, predictions: np.ndarray, coordinates: Optional[np.ndarray]) -> Dict[str, Any]`: Generate spatial explanation for geospatial predictions.

### GeospatialModelEvaluator
 Evaluate geospatial AI models with spatial-specific metrics.

**Methods**:
- `evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray, labels: Optional[List]) -> Dict[str, float]`: Evaluate classification model.
- `evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]`: Evaluate regression model.
- `evaluate_spatial_accuracy(y_true: np.ndarray, y_pred: np.ndarray, coordinates: np.ndarray, buffer_distance: float) -> Dict[str, float]`: Evaluate spatial accuracy (location-based metrics).
- `cross_validate_spatial(model: Any, X: np.ndarray, y: np.ndarray, coordinates: np.ndarray, n_splits: int) -> Dict[str, float]`: Perform spatial cross-validation.

### TrainingConfig
 Configuration for model training.

### ModelTrainer
 Trainer for geospatial AI models with evaluation.

**Methods**:
- `train_classifier(model: Any, X_train: np.ndarray, y_train: np.ndarray, X_val: Optional[np.ndarray], y_val: Optional[np.ndarray]) -> Dict[str, Any]`: Train a classification model.
- `train_regressor(model: Any, X_train: np.ndarray, y_train: np.ndarray, X_val: Optional[np.ndarray], y_val: Optional[np.ndarray]) -> Dict[str, Any]`: Train a regression model.
- `evaluate_model(model: Any, X_test: np.ndarray, y_test: np.ndarray, task_type: str) -> Dict[str, Any]`: Evaluate a trained model on test data.
- `load_model(path: Union[str, Path]) -> Any`: Load a trained model from disk (supports both joblib and pickle formats).

## Capabilities

- **4 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-AI/src/geo_infer_ai/core`
- **Type**: Directory Node
