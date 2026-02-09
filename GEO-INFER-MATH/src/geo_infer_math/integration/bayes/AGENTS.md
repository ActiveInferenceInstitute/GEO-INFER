# Agent
: bayes

## Scope
 This directory contains bayes components for the module. It provides 5 classes and 0 functions.

## Classes
 and Functions

### BayesianOptimization
 Bayesian optimization tools.

**Methods**:
- `optimize(objective, prior, **kwargs)`:

### MCMCHelpers
 MCMC algorithm helpers.

**Methods**:
- `mcmc_sample(log_posterior, initial_state, **kwargs)`:

### ModelSelection
 Bayesian model selection.

**Methods**:
- `select_model(models, data, **kwargs)`:

### PosteriorHelpers
 Posterior distribution helpers.

**Methods**:
- `calculate_posterior(prior, likelihood, data, **kwargs)`:

### PriorBuilders
 Prior distribution construction tools.

**Methods**:
- `build_prior(distribution_type, **kwargs)`:

## Capabilities

- **5 classes** for core functionality

## Integration

- **Location**: `src/geo_infer_math/integration/bayes`
- **Type**: Directory Node
