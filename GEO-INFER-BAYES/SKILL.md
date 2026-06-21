---
name: geo-infer-bayes
description: Bayesian inference and probabilistic modeling for geospatial data. Use when building hierarchical models, computing posteriors with PyMC or TFP, performing variational inference, model comparison (LOO/WAIC/DIC), or spatial Gaussian processes.
prerequisites:
  required:
    - geo-infer-math
  recommended:
    - geo-infer-space
    - geo-infer-data
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-BAYES

## Instructions

### Core Capabilities

- **Bayesian inference**: Full posterior computation via MCMC and variational methods
- **Model comparison**: LOO-CV, WAIC, DIC, BIC, AIC (all real implementations)
- **Gaussian processes**: Cholesky-decomposition GP with multiple kernels
- **Hierarchical models**: Partial pooling via Cholesky LKJ decomposition
- **Prior specification**: Jeffreys, reference, unit-information priors
- **ELBO computation**: Real evidence lower bound (not placeholder)

### Key Imports

```python
from geo_infer_bayes.core.bayesian_inference import BayesianModel
from geo_infer_bayes.core.gaussian_process import GaussianProcess
from geo_infer_bayes.core.variational import VariationalInference
from geo_infer_bayes.api.pymc_interface import PyMCInterface
from geo_infer_bayes.api.tfp_interface import TFPInterface
```

## Examples

```python
from geo_infer_bayes.core.bayesian_inference import BayesianModel

model = BayesianModel(prior="normal", likelihood="normal")
posterior = model.fit(data, n_samples=2000)
comparison = model.compare(["model_a", "model_b"], method="loo")
```

## Guidelines

- GP uses actual Cholesky decomposition
- TFP interface: real GP + Metropolis-Hastings sampling
- PyMC interface: posterior predictive sampling for predictions
- Variational: real ELBO computation with KL divergence
- Test: `uv run python -m pytest GEO-INFER-BAYES/tests/ -v`

### Integrations

- **ACT** → Active Inference belief updating and free energy
- **MATH** → Spatial statistics feeding Bayesian models
- **SPM** → Bayesian GLM fitting for parametric maps
- **AI** → Bayesian hyperparameter optimization
- **RISK** → Bayesian uncertainty quantification for risk
