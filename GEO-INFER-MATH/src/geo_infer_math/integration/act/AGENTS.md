# Agent
: act

## Scope
 This directory contains act components for the module. It provides 5 classes and 0 functions.

## Classes
 and Functions

### BeliefUpdating
 Belief updating for Active Inference.

**Methods**:
- `update(current_beliefs, new_observations, **kwargs)`:

### FreeEnergyCalculator
 Free energy calculations for Active Inference.

**Methods**:
- `calculate(observations, beliefs, **kwargs)`:

### GenerativeModels
 Generative model construction tools.

**Methods**:
- `create_generative_model(model_type, parameters, **kwargs)`:

### PolicyOptimization
 Policy optimization for Active Inference.

**Methods**:
- `optimize_policy(policy_function, initial_policy, **kwargs)`:

### VariationalInferenceHelpers
 Variational inference helpers.

**Methods**:
- `perform_vi(observations, prior, **kwargs)`:

## Capabilities

- **5 classes** for core functionality

## Integration

- **Location**: `src/geo_infer_math/integration/act`
- **Type**: Directory Node
