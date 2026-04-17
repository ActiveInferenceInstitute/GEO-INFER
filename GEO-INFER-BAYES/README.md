---
title: "GEO-INFER-BAYES: Bayesian Inference for Geospatial Applications"
description: "Bayesian inference framework with probabilistic modeling, uncertainty quantification, and computational methods for geospatial data"
purpose: "Enable inference and decision-making under uncertainty for geospatial applications"
module_type: "Analytical Core"
status: "Beta"
last_updated: "2026-04-16"
dependencies: ["MATH"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-ACT", "GEO-INFER-AI"]
tags: ["bayesian", "inference", "uncertainty", "probabilistic", "mcmc", "hierarchical"]
difficulty: "Advanced"
estimated_time: "60"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-BAYES: Bayesian Inference for Geospatial Applications

> **Purpose**: Enable inference and decision-making under uncertainty for geospatial applications
>
> This module provides Bayesian inference capabilities with probabilistic modeling, uncertainty quantification, and computational methods for geospatial data analysis.

## Overview

Note: Code examples are illustrative; see `GEO-INFER-BAYES/examples` for runnable scripts.

### Links
- Module README: ../../GEO-INFER-BAYES/README.md
- Modules Overview: ../modules/index.md

GEO-INFER-BAYES provides a framework for Bayesian inference processes within the GEO-INFER ecosystem, implementing probabilistic modeling, uncertainty quantification, and Bayesian computational methods for geospatial applications.

## Core Objectives

- **Probabilistic Modeling**: Implement Bayesian models for spatial and spatio-temporal data
- **Uncertainty Quantification**: Provide methods for quantifying and propagating uncertainty
- **Inference Methods**: Support multiple inference algorithms (MCMC, HMC, VI, SMC, ABC)
- **Model Comparison**: Enable model selection and comparison using information criteria
- **Integration**: Seamless integration with Active Inference, spatial analysis, and domain modules

## Core Features

- **Spatial Gaussian Processes**: RBF, Matern, and Exponential kernels for spatial interpolation
- **Spatio-Temporal Models**: Temporal extensions for time-series geospatial data
- **Hierarchical Bayesian Models**: Multi-level models for nested spatial structures
- **Inference Methods**: MCMC, HMC, Variational Inference, SMC, and ABC
- **Posterior Analysis**: Uncertainty quantification, credible intervals, and visualization
- **Model Comparison**: WAIC, LOO-CV, and Bayes factors for model selection
- **API Interfaces**: Integration with PyMC, Stan, and TensorFlow Probability

## Installation

### Install (monorepo)

```bash
uv pip install -e ./GEO-INFER-BAYES
```

### Development Installation

```bash
git clone https://github.com/your-organization/GEO-INFER.git
cd GEO-INFER/GEO-INFER-BAYES
uv pip install -e .
```

## Quick Start

```python
from geo_infer_bayes import SpatialGP, BayesianInference

# Create spatial Gaussian Process model
gp = SpatialGP(kernel='matern', lengthscale=1.0, variance=1.0)

# Initialize inference engine
inference = BayesianInference(model=gp, method='mcmc')

# Run inference
posterior = inference.sample(
    data=observations,
    spatial_coords=locations,
    n_samples=1000
)

# Predict with uncertainty
predictions, std = posterior.predict_spatial(
    grid=target_locations,
    return_uncertainty=True
)
```

See `examples/` directory for complete runnable scripts.

## Module Structure

```
GEO-INFER-BAYES/
├── config/               # Configuration files
├── docs/                 # Documentation
├── examples/             # Example use cases
├── src/                  # Source code
│   └── geo_infer_bayes/  # Main package
│       ├── api/          # API definitions (PyMC, Stan, TFP interfaces)
│       ├── core/         # Core functionality (inference engines)
│       ├── models/       # Bayesian models
│       └── utils/        # Utility functions
└── tests/                # Test suite
```

## Bayesian Models

### Spatial Gaussian Processes

Gaussian Process models for spatial interpolation with various kernels:

```python
from geo_infer_bayes.models import SpatialGP

# RBF kernel
model_rbf = SpatialGP(kernel='rbf', lengthscale=1.0, variance=1.0)

# Matern kernel
model_matern = SpatialGP(kernel='matern', lengthscale=1.0, degree=1.5)

# Exponential kernel
model_exp = SpatialGP(kernel='exponential', lengthscale=1.0)
```

### Hierarchical Bayesian Models

Models for multi-level spatial data:

```python
from geo_infer_bayes.models import HierarchicalBayesianModel

# Create hierarchical model
model = HierarchicalBayesianModel(n_levels=2)
```

### Dirichlet Process Mixtures

For spatial clustering:

```python
from geo_infer_bayes.models import DirichletProcessMixture

# Create mixture model
model = DirichletProcessMixture(alpha=1.0)
```

## Inference Methods

### Markov Chain Monte Carlo (MCMC)

```python
from geo_infer_bayes.core import BayesianInference

inference = BayesianInference(model=model, method='mcmc')
posterior = inference.run(
    data=data,
    n_samples=1000,
    n_warmup=500,
    thin=1
)
```

### Hamiltonian Monte Carlo (HMC)

```python
inference = BayesianInference(model=model, method='hmc')
posterior = inference.run(
    data=data,
    n_samples=1000,
    n_warmup=500
)
```

### Variational Inference (VI)

```python
# Mean-field VI is supported; full-rank VI raises NotImplementedError
# until reparameterized covariance-factor gradients land.
inference = BayesianInference(
    model=model,
    method='vi',
    vi_method='meanfield',
)
posterior = inference.run(
    data=data,
    n_iterations=10000,
)
```

## Posterior Analysis

```python
# Summary statistics
summary = posterior.summary()
print(summary)

# Credible intervals
lower, upper = posterior.credible_interval('lengthscale', alpha=0.05)  # 95% CI

# Visualization
posterior.plot_trace()
posterior.plot_posterior()
posterior.plot_forest()

# Spatial prediction with uncertainty
fig, ax = posterior.plot_spatial_prediction(grid=grid_points, uncertainty=True)
```

## API Interfaces

### PyMC Interface

```python
from geo_infer_bayes.api import PyMCInterface

# Create PyMC model
pymc_interface = PyMCInterface()
model = pymc_interface.create_spatial_gp_model(X, y, kernel_type='matern')

# Sample using PyMC
trace = pymc_interface.sample(n_samples=1000, n_warmup=500)

# Convert to GEO-INFER-BAYES format
samples = pymc_interface.convert_to_geo_infer_format(trace)
```

### Stan Interface

```python
from geo_infer_bayes.api import StanInterface

# Create Stan model
stan_interface = StanInterface()
model = stan_interface.create_spatial_gp_model(X, y)

# Sample using Stan
samples = stan_interface.sample(n_samples=1000, n_warmup=500)
```

## API Reference

### Core Classes

#### BayesianInference

Main Bayesian inference engine.

```python
from geo_infer_bayes import BayesianInference

# Initialize inference engine
inference = BayesianInference(
    method='mcmc',
    sampler='nuts',
    draws=2000
)

# Define model
model = inference.define_model(
    likelihood=normal_likelihood,
    priors=prior_distributions
)

# Run inference
posterior = inference.sample(
    model=model,
    data=observed_data
)
```

#### SpatialGP

Spatial Gaussian Process models.

```python
from geo_infer_bayes import SpatialGP

# Create spatial GP with RBF kernel
gp = SpatialGP(
    kernel='rbf',
    lengthscale=1.0,
    variance=1.0
)

# Fit model
gp.fit(
    X=spatial_coordinates,
    y=observations
)

# Predict with uncertainty
predictions, std = gp.predict(
    X_new=new_locations,
    return_std=True
)
```

#### PosteriorAnalysis

Posterior distribution analysis and visualization.

```python
from geo_infer_bayes import PosteriorAnalysis

# Initialize posterior analysis
analysis = PosteriorAnalysis(posterior_samples)

# Summary statistics
summary = analysis.summary()

# Trace plots
analysis.plot_trace()

# Posterior predictive checks
ppc = analysis.posterior_predictive_check(observed_data)
```

#### HierarchicalBayesianModel

Multi-level hierarchical Bayesian models.

```python
from geo_infer_bayes.models import HierarchicalBayesianModel

# Create hierarchical model
hierarchical = HierarchicalBayesianModel(
    n_levels=3,
    spatial_structure='hierarchical'
)

# Define model structure
hierarchical.define_levels(
    level_1='individual',
    level_2='region',
    level_3='country'
)

# Fit model
results = hierarchical.fit(data=multi_level_data)
```

### Inference Methods

```python
from geo_infer_bayes.core.inference import (
    run_mcmc,
    run_variational_inference,
    run_laplace_approximation
)

# MCMC sampling
posterior = run_mcmc(
    model=model,
    draws=2000,
    chains=4
)

# Variational inference
vi_posterior = run_variational_inference(
    model=model,
    n_samples=1000
)
```

## Integration with Other Modules

GEO-INFER-BAYES integrates with other GEO-INFER modules:

- **GEO-INFER-SPACE**: For spatial data structures and operations
- **GEO-INFER-TIME**: For temporal components in Bayesian models
- **GEO-INFER-ACT**: For active inference and decision-making
- **GEO-INFER-SIM**: For Bayesian emulation of simulations
- **GEO-INFER-AGENT**: For Bayesian agent-based models

## Examples

See the `examples/` directory for complete usage examples:

- `spatial_gp_example.py`: Spatial Gaussian Process modeling
- `hierarchical_example.py`: Hierarchical Bayesian modeling
- `mixture_example.py`: Dirichlet Process mixture modeling
- `spatiotemporal_example.py`: Spatio-temporal modeling

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_spatial_gp.py
```

## Documentation

For full documentation, see the `docs/` directory or visit the [online documentation](https://your-organization.github.io/GEO-INFER-BAYES/).

## Contributing

Please read the [Contributing Guidelines](../../README.md#-contributing) for details on contributing to this module.

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |

## License

This project is licensed under the terms of the LICENSE file included in the main GEO-INFER repository. 