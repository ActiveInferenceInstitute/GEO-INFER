# Agent
: ai

## Scope
 This directory contains ai components for the module. It provides 5 classes and 0 functions.

## Classes
 and Functions

### AIGradientHelpers
 Gradient computation helpers for spatial ML.

**Methods**:
- `compute_spatial_gradient(function: Callable, parameters: np.ndarray, spatial_context: Optional[np.ndarray], method: str) -> np.ndarray`: Compute gradient with spatial context.
- `compute_hessian(function: Callable, parameters: np.ndarray, epsilon: float) -> np.ndarray`: Compute Hessian matrix.
- `compute_gradient_with_regularization(function: Callable, parameters: np.ndarray, regularization: float, reg_type: str) -> np.ndarray`: Compute gradient with regularization.

### SpatialLossFunctions
 Spatial loss functions for neural networks.

**Methods**:
- `calculate_loss(predictions, targets, coordinates, **kwargs)`:

### OptimizationBridges
 Bridge between MATH optimization and AI training.

**Methods**:
- `bridge_optimize(objective, initial_guess, **kwargs)`:

### SpatialAttention
 Mathematical foundations for spatial attention.

**Methods**:
- `compute_attention_weights(queries, keys, values, **kwargs)`:

### TensorOperations
 Tensor operations for AI models.

**Methods**:
- `spatial_tensor_operation(tensor, operation, **kwargs)`:

## Capabilities

- **5 classes** for core functionality

## Integration

- **Location**: `src/geo_infer_math/integration/ai`
- **Type**: Directory Node
