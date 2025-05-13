# GEO-INFER-BAYES

Bayesian inference for geospatial applications within the GEO-INFER ecosystem.

## Overview

GEO-INFER-BAYES provides a comprehensive framework for Bayesian inference processes within the GEO-INFER ecosystem. This module implements probabilistic modeling, uncertainty quantification, and Bayesian computational methods specifically tailored for geospatial applications, enabling robust inference and decision-making under uncertainty.

## Key Features

- **Hierarchical Bayesian models** for spatial and spatio-temporal data
- **Bayesian computational methods** (MCMC, HMC, VI, SMC)
- **Probabilistic programming interfaces** to PyMC, Stan, and TensorFlow Probability
- **Bayesian model comparison and selection**
- **Spatial priors and likelihood functions** for geospatial applications

## Installation

### From PyPI

```bash
pip install geo-infer-bayes
```

### Development Installation

```bash
git clone https://github.com/your-organization/GEO-INFER.git
cd GEO-INFER/GEO-INFER-BAYES
pip install -e .
```

## Quick Start

```python
from geo_infer_bayes.models import SpatialGP
from geo_infer_bayes.core import BayesianInference
import numpy as np

# Generate synthetic data
X = np.random.uniform(0, 10, size=(50, 2))  # 50 points in 2D space
y = np.sin(X[:, 0]) * np.cos(X[:, 1]) + np.random.normal(0, 0.1, size=50)  # Target with noise

# Define spatial model
model = SpatialGP(kernel='rbf', lengthscale=1.0, variance=1.0, noise=0.1)

# Perform Bayesian inference
inference = BayesianInference(model=model, method='mcmc')
posterior = inference.run(data={'X': X, 'y': y})

# Make predictions with uncertainty
X_new = np.random.uniform(0, 10, size=(10, 2))  # 10 new points
mean, std = posterior.predict(X_new, return_std=True)

# Visualize results
posterior.plot_posterior()
posterior.plot_trace()
```

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
inference = BayesianInference(model=model, method='vi')
posterior = inference.run(
    data=data,
    n_iterations=10000
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

Please read [CONTRIBUTING.md](../CONTRIBUTING.md) for details on contributing to this module.

## License

This project is licensed under the terms of the LICENSE file included in the main GEO-INFER repository. 