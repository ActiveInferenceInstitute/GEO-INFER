# GEO-INFER-BAYES: Bayesian Inference Framework

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview

The GEO-INFER-BAYES module provides Bayesian inference capabilities that enable agents to perform probabilistic reasoning, uncertainty quantification, and belief updating within the GEO-INFER framework. It serves as the mathematical foundation for Active Inference agents and supports decision-making under uncertainty.

## Implementation Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational.

### Currently Implemented

- ✅ **BayesianInference**: Core inference engine supporting MCMC, HMC, VI, SMC, and ABC
- ✅ **SpatialGP**: Spatial Gaussian Process models with multiple kernel types
- ✅ **SpatioTemporalGP**: Spatio-temporal Gaussian Process models
- ✅ **HierarchicalBayesianModel**: Multi-level hierarchical models
- ✅ **PosteriorAnalysis**: Posterior distribution analysis and visualization
- ✅ **ModelComparison**: Bayesian model comparison and selection
- ✅ **API Interfaces**: PyMC, Stan, and TensorFlow Probability interfaces

### Aspirational/Planned Features

- 🔮 **BayesianAgent**: Autonomous agent with Bayesian belief updating
- 🔮 **AdaptiveSamplingAgent**: Optimal data collection strategies
- 🔮 **UncertaintyReductionAgent**: Targeted uncertainty minimization

## Technical Capabilities

### Core Classes

#### Bayesian Inference

- **`BayesianInference`**: `BayesianInference(**kwargs)`
  - Core Bayesian inference engine
  - Methods:
   
- `sample(data, method='mcmc', **kwargs) -> Dict[str, Any]`
   
- `fit(model, data, **kwargs) -> PosteriorDistribution`

- **`MCMC`**: `MCMC(**kwargs)`
  - Markov Chain Monte Carlo sampling
  - Methods: `sample(model, data, draws=2000, chains=4) -> Trace`

- **`HMC`**: `HMC(**kwargs)`
  - Hamiltonian Monte Carlo sampling
  - Methods: `sample(model, data, **kwargs) -> Trace`

- **`VariationalInference`**: `VariationalInference(**kwargs)`
  - Variational inference methods
  - Methods: `fit(model, data, **kwargs) -> ApproximatePosterior`

- **`SequentialMonteCarlo`**: `SequentialMonteCarlo(**kwargs)`
  - Sequential Monte Carlo methods
  - Methods: `sample(model, data, **kwargs) -> Particles`

- **`ApproximateBayesianComputation`**: `ApproximateBayesianComputation(**kwargs)`
  - ABC inference methods
  - Methods: `sample(model, data, **kwargs) -> Posterior`

#### Spatial Models

- **`SpatialGP`**: `SpatialGP(kernel='rbf', lengthscale=1.0, variance=1.0, **kwargs)`
  - Spatial Gaussian Process models
  - Methods:
   
- `fit(X, y, **kwargs) -> None`
   
- `predict(X_new, return_std=True) -> Tuple[np.ndarray, np.ndarray]`

- **`SpatioTemporalGP`**: `SpatioTemporalGP(spatial_kernel='matern', temporal_kernel='rbf', **kwargs)`
  - Spatio-temporal Gaussian Process models
  - Methods:
   
- `fit(X_spatial, X_temporal, y, **kwargs) -> None`
   
- `predict(X_spatial_new, X_temporal_new, return_std=True) -> Tuple[np.ndarray, np.ndarray]`

#### Analysis and Comparison

- **`PosteriorAnalysis`**: `PosteriorAnalysis(posterior, **kwargs)`
  - Posterior distribution analysis
  - Methods:
   
- `credible_interval(parameter, alpha=0.05) -> Tuple[float, float]`
   
- `predict_spatial(grid, return_uncertainty=True) -> Tuple[np.ndarray, np.ndarray]`
   
- `summary() -> Dict[str, Any]`

- **`ModelComparison`**: `ModelComparison(**kwargs)`
  - Bayesian model comparison
  - Methods:
   
- `compare_models(models, data, criterion='waic') -> Dict[str, Dict[str, Any]]`
   
- `select_best_model(model_scores) -> Model`

- **`HierarchicalBayesianModel`**: `HierarchicalBayesianModel(n_levels, spatial_structure='hierarchical', **kwargs)`
  - Hierarchical Bayesian models
  - Methods:
   
- `define_levels(**level_definitions) -> None`
   
- `fit(data, spatial_hierarchy, **kwargs) -> PosteriorDistribution`

## Agent Capabilities Supported

### 1. Belief Updating

BAYES provides probabilistic belief updating for agents:

```python
from geo_infer_bayes import BayesianInference, SpatialGP

# Create spatial GP model for agent beliefs
gp = SpatialGP(
    kernel='matern',
    lengthscale=1.0,
    variance=1.0)

# Initialize inference engine
inference = BayesianInference(
    model=gp,
    method='mcmc',
    sampler_config={'draws': 2000, 'chains': 4})

# Agent updates beliefs from observations
posterior = inference.sample(
    data=agent_observations,
    spatial_coords=agent_locations)

# Extract updated beliefs
updated_beliefs = posterior.summary()```

### 2. Uncertainty Quantification

BAYES enables agents to quantify and reason about uncertainty:

```python
from geo_infer_bayes import PosteriorAnalysis

# Analyze posterior uncertainty
analysis = PosteriorAnalysis(posterior)

# Get credible intervals
lower, upper = analysis.credible_interval('lengthscale', alpha=0.05)

# Spatial prediction with uncertainty
predictions, std = analysis.predict_spatial(
    grid=target_locations,
    return_uncertainty=True)

# Agent uses uncertainty for decision-making
if std.max() > uncertainty_threshold:
    agent.collect_additional_data()```

### 3. Hierarchical Modeling

BAYES supports hierarchical models for multi-scale agent reasoning:

```python
from geo_infer_bayes.models import HierarchicalBayesianModel

# Create hierarchical model for multi-level reasoning
hierarchical = HierarchicalBayesianModel(
    n_levels=3,
    spatial_structure='hierarchical')

# Define hierarchical structure
hierarchical.define_levels(
    level_1='local',
    level_2='regional',
    level_3='global')

# Agent reasons across multiple scales
results = hierarchical.fit(
    data=multi_scale_observations,
    spatial_hierarchy=agent_spatial_structure)
```

### 4. Model Comparison

BAYES enables agents to compare and select models:

```python
from geo_infer_bayes.core import ModelComparison

# Compare multiple models
comparison = ModelComparison()

# Agent evaluates model alternatives
model_scores = comparison.compare_models(
    models=[gp_rbf, gp_matern, gp_exponential],
    data=validation_data,
    criterion='waic' 

# Widely Applicable Information Criterion)

# Select best model
best_model = comparison.select_best_model(model_scores)```

## Integration with Active Inference

BAYES integrates with GEO-INFER-ACT for Active Inference agents:

```python
from geo_infer_bayes import BayesianInference
from geo_infer_act import ActiveInferenceModel

# Bayesian inference for belief updating
bayes_inference = BayesianInference(model=generative_model, method='vi')

# Active Inference for action selection
act_model = ActiveInferenceModel(
    state_dim=10,
    obs_dim=5,
    action_dim=3)

# Agent combines Bayesian updating with Active Inference
# 1. Update beliefs via Bayesian inference
posterior = bayes_inference.sample(observations=agent_observations)

# 2. Select actions via Active Inference
action = act_model.act(observation=current_observation)```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Bayesian Inference** | ✅ Ready | MCMC, HMC, VI, SMC, ABC methods |
| **Spatial GP Models** | ✅ Ready | RBF, Matern, Exponential kernels |
| **Spatio-Temporal GP** | ✅ Ready | Temporal extensions for time series |
| **Hierarchical Models** | ✅ Ready | Multi-level spatial modeling |
| **Posterior Analysis** | ✅ Ready | Uncertainty quantification |
| **Model Comparison** | ✅ Ready | WAIC, LOO-CV, Bayes factors |
| **API Interfaces** | ✅ Ready | PyMC, Stan, TFP integration |
| **Bayesian Agent** | 🔮 Planned | Autonomous Bayesian agent |
| **Adaptive Sampling** | 🔮 Planned | Optimal data collection |

## Use Cases

### 1. Environmental Monitoring Agents

```python
from geo_infer_bayes import SpatialGP, BayesianInference

# Agent monitors environmental variables
monitoring_gp = SpatialGP(kernel='matern', lengthscale=5.0)
inference = BayesianInference(model=monitoring_gp, method='mcmc')

# Update beliefs from sensor readings
posterior = inference.sample(
    data=sensor_readings,
    spatial_coords=sensor_locations)

# Predict environmental conditions with uncertainty
predictions, uncertainty = posterior.predict_spatial(
    grid=monitoring_grid,
    return_uncertainty=True)
```

### 2. Risk Assessment Agents

```python
from geo_infer_bayes.models import HierarchicalBayesianModel

# Agent assesses risk across multiple scales
risk_model = HierarchicalBayesianModel(n_levels=2)
risk_model.define_levels(level_1='property', level_2='region')

# Fit hierarchical risk model
risk_posterior = risk_model.fit(
    data=risk_indicators,
    spatial_hierarchy=administrative_boundaries)

# Quantify risk uncertainty
risk_estimates = risk_posterior.summary()```

### 3. Predictive Agents

```python
from geo_infer_bayes.models import SpatioTemporalGP

# Agent predicts future spatial patterns
st_gp = SpatioTemporalGP(
    spatial_kernel='matern',
    temporal_kernel='rbf',
    lengthscale_spatial=1.0,
    lengthscale_temporal=0.5)

# Fit spatio-temporal model
st_gp.fit(
    X_spatial=spatial_coords,
    X_temporal=time_points,
    y=observations)

# Forecast future states
forecast, forecast_std = st_gp.predict(
    X_spatial_new=future_locations,
    X_temporal_new=future_times,
    return_std=True)
```

---

This AGENTS.md documents how GEO-INFER-BAYES provides Bayesian inference capabilities for intelligent agents within the GEO-INFER framework.
