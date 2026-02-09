# Agent
: models

## Scope
 This directory contains models components for the module. It provides 3 classes and 0 functions.

## Classes
 and Functions

### ConcreteAgricultureModel
 Concrete implementation of AgricultureModel for testing.

**Methods**:
- `predict(data: Dict[str, Any]) -> Dict[str, Any]`: Implement the predict method for testing.

### TestAgricultureModel
 Test suite for AgricultureModel class.

**Methods**:
- `test_initialization()`: Test initialization of AgricultureModel.
- `test_validate_inputs()`: Test input validation.
- `test_predict()`: Test predict method.
- `test_info()`: Test info property.
- `test_save_load_not_implemented()`: Test that save and load methods raise NotImplementedError.

### TestCropYieldModel
 Test suite for CropYieldModel class.

**Methods**:
- `test_initialization()`: Test initialization of CropYieldModel.
- `test_fit_machine_learning()`: Test fitting a machine learning model.
- `test_predict_machine_learning()`: Test making predictions with a machine learning model.
- `test_predict_statistical()`: Test making predictions with a statistical model.
- `test_predict_process_based()`: Test making predictions with a process-based model.
- `test_get_feature_importance()`: Test getting feature importance from a trained model.
- `test_save_load()`: Test saving and loading a model.

## Capabilities

- **3 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-AG/tests/unit/models`
- **Type**: Directory Node
