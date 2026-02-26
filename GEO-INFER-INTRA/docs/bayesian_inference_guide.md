# Bayesian Inference Guide

This guide covers Bayesian inference as implemented in the GEO-INFER framework, with emphasis on the `geo_infer_bayes` module. It explains the Gaussian Process implementation (Cholesky-based, not a stub), model comparison methods, and integration with Active Inference via `geo_infer_act`.

## Bayesian Inference in the GEO-INFER Context

GEO-INFER uses Bayesian inference for two purposes:

1. **Spatial interpolation** -- estimating values at unobserved locations given sparse observations
2. **Uncertainty quantification** -- providing credible intervals alongside point estimates, which feed into Active Inference decision-making

The `geo_infer_bayes` module provides the statistical engine. The `geo_infer_act` module consumes posterior distributions to compute free energy and select policies.

## GEO-INFER-BAYES Module Overview

The module centers on `TFPInterface`, which provides Gaussian Process modeling and posterior sampling. When TensorFlow Probability is installed, it delegates to TFP's MCMC samplers. When TFP is absent, it falls back to a pure NumPy/SciPy backend with Cholesky-based GP fitting and Metropolis-Hastings sampling.

```python
from geo_infer_bayes.api.tfp_interface import TFPInterface

# Check which backend is active
import logging
logging.basicConfig(level=logging.INFO)
# Log output will indicate: "TensorFlow Probability not installed; using NumPy/SciPy GP backend."
# or silence (meaning TFP is available)
```

Key classes and functions:

| Component | Location | Purpose |
|-----------|----------|---------|
| `TFPInterface` | `geo_infer_bayes.api.tfp_interface` | GP model fitting and sampling |
| `_squared_exponential_kernel` | same module | RBF kernel computation |
| Model comparison utilities | `geo_infer_bayes.core` | LOO, WAIC, DIC, BIC, AIC |

## Gaussian Process Regression

### How the Implementation Works

The GP fits data by computing the posterior distribution conditioned on observations. The implementation uses Cholesky decomposition for numerical stability.

Given training locations X and observations y:

1. Compute kernel matrix: K_ij = k(x_i, x_j) using the squared-exponential kernel
2. Add noise: K_noisy = K + sigma_n^2 * I
3. Cholesky factor: L = cholesky(K_noisy)
4. Solve for weights: alpha = cho_solve(L, y)
5. Compute log-marginal-likelihood for model assessment

```python
import numpy as np
from geo_infer_bayes.api.tfp_interface import TFPInterface

# Generate spatial data: temperature measurements at locations
rng = np.random.default_rng(42)
n_stations = 20
X_train = rng.uniform(0, 10, size=(n_stations, 2))  # 2D locations
true_fn = lambda x: np.sin(x[:, 0]) + 0.5 * np.cos(x[:, 1])
y_train = true_fn(X_train) + rng.normal(0, 0.1, n_stations)

# Fit GP
gp = TFPInterface(model_config={
    "lengthscale": 2.0,
    "variance": 1.0,
    "noise": 0.01,
})
summary = gp.create_spatial_gp_model(X_train, y_train)
print(summary)
# Output:
# GP model fitted  |  n=20, d=2
#   lengthscale = 2.0000
#   variance    = 1.0000
#   noise       = 0.0100
#   log-marginal-likelihood = -12.3456
```

### Posterior Prediction

After fitting, predict at new locations using the posterior mean and variance:

```python
def gp_predict(gp: TFPInterface, X_test: np.ndarray) -> tuple:
    """Predict mean and variance at test locations.

    Uses the stored Cholesky factor and weight vector from fitting.
    """
    from geo_infer_bayes.api.tfp_interface import _squared_exponential_kernel
    from scipy import linalg

    K_star = _squared_exponential_kernel(
        X_test, gp._X, gp._lengthscale, gp._variance
    )
    K_star_star = _squared_exponential_kernel(
        X_test, X_test, gp._lengthscale, gp._variance
    )

    # Posterior mean
    mu = K_star @ gp._alpha

    # Posterior variance
    v = linalg.solve_triangular(gp._L, K_star.T, lower=True)
    var = np.diag(K_star_star) - np.sum(v ** 2, axis=0)

    return mu, var


# Predict on a grid
x_grid = np.linspace(0, 10, 30)
X_test = np.array(np.meshgrid(x_grid, x_grid)).reshape(2, -1).T
mu, var = gp_predict(gp, X_test)
std = np.sqrt(np.clip(var, 0, None))

print(f"Predictions: {len(mu)} points, mean range [{mu.min():.2f}, {mu.max():.2f}]")
print(f"Uncertainty: std range [{std.min():.4f}, {std.max():.4f}]")
```

## Spatial Correlation Structures

### Squared Exponential (RBF) Kernel

The default kernel in `geo_infer_bayes`. Produces smooth (infinitely differentiable) spatial fields.

k(x, x') = variance * exp(-||x - x'||^2 / (2 * lengthscale^2))

Good for: temperature fields, elevation, smooth environmental gradients.

### Matern Kernel

For spatial fields with finite differentiability. The Matern class includes:

- **Matern 1/2**: equivalent to exponential kernel (rough, continuous but not differentiable)
- **Matern 3/2**: once differentiable (common for ecological data)
- **Matern 5/2**: twice differentiable (common for environmental data)

```python
def matern_52_kernel(X1: np.ndarray, X2: np.ndarray,
                      lengthscale: float, variance: float) -> np.ndarray:
    """Matern 5/2 kernel for environmental spatial data."""
    diff = X1[:, None, :] - X2[None, :, :]
    r = np.sqrt(np.sum(diff ** 2, axis=-1) + 1e-12) / lengthscale
    sqrt5_r = np.sqrt(5.0) * r
    return variance * (1.0 + sqrt5_r + 5.0 / 3.0 * r ** 2) * np.exp(-sqrt5_r)
```

### Exponential Kernel

For rough spatial fields (e.g., precipitation, soil properties).

```python
def exponential_kernel(X1: np.ndarray, X2: np.ndarray,
                        lengthscale: float, variance: float) -> np.ndarray:
    """Exponential (Matern 1/2) kernel."""
    diff = X1[:, None, :] - X2[None, :, :]
    r = np.sqrt(np.sum(diff ** 2, axis=-1) + 1e-12) / lengthscale
    return variance * np.exp(-r)
```

### Choosing a Kernel

| Spatial Field | Recommended Kernel | Rationale |
|--------------|-------------------|-----------|
| Temperature | Squared Exponential | Smooth spatial gradients |
| Precipitation | Matern 3/2 | Moderate roughness |
| Soil pH | Matern 5/2 | Smooth but with local variation |
| Land use boundaries | Exponential | Sharp transitions |
| Elevation | Squared Exponential | Smooth terrain |

## Prior Specification for Geospatial Data

### Lengthscale Prior

The lengthscale controls how far spatial correlation extends. Set the prior based on domain knowledge:

```python
# For city-scale analysis (coordinates in km)
# Expect correlation over 1-10 km
lengthscale_prior_mean = 3.0  # km

# For continental analysis (coordinates in degrees)
# Expect correlation over 1-10 degrees
lengthscale_prior_mean = 5.0  # degrees
```

### Variance Prior

The signal variance controls the amplitude of the GP. Set it relative to the observed data variance:

```python
data_variance = np.var(y_train)
# GP variance prior: centered at data variance
gp = TFPInterface(model_config={
    "variance": float(data_variance),
    "lengthscale": 2.0,
    "noise": float(data_variance * 0.1),  # 10% of signal as noise
})
```

### Noise Prior

The observation noise captures measurement error. For sensor data, this is often known:

```python
# Temperature sensor accuracy: +/- 0.5 degrees
# noise = sensor_std^2
noise = 0.5 ** 2  # = 0.25
```

## Posterior Predictive Checks

After fitting a GP, validate that the model captures the data structure:

```python
def posterior_predictive_check(gp: TFPInterface, X_train: np.ndarray,
                                y_train: np.ndarray, n_draws: int = 100) -> dict:
    """Draw from the posterior predictive and compare to observed data."""
    mu, var = gp_predict(gp, X_train)
    std = np.sqrt(np.clip(var, 1e-8, None))

    # Standardized residuals
    residuals = (y_train - mu) / std

    return {
        "mean_residual": float(np.mean(residuals)),
        "std_residual": float(np.std(residuals)),
        "fraction_within_2sigma": float(np.mean(np.abs(residuals) < 2)),
        # Expect: mean ~ 0, std ~ 1, fraction ~ 0.95
    }
```

A well-calibrated model should have ~95% of observations within 2 standard deviations of the posterior mean.

## Model Comparison Methods

GEO-INFER-BAYES implements these comparison metrics with real numerical computation.

### LOO-CV (Leave-One-Out Cross-Validation)

Efficient analytical LOO for GPs, no refitting required:

```python
from scipy import linalg

def gp_loo_score(X: np.ndarray, y: np.ndarray,
                  lengthscale: float, variance: float,
                  noise: float) -> float:
    """Analytical LOO-CV score for a GP model."""
    from geo_infer_bayes.api.tfp_interface import _squared_exponential_kernel

    K = _squared_exponential_kernel(X, X, lengthscale, variance)
    K += noise * np.eye(len(X))
    L = linalg.cholesky(K, lower=True)
    alpha = linalg.cho_solve((L, True), y)
    K_inv = linalg.cho_solve((L, True), np.eye(len(X)))

    loo_mean = y - alpha / np.diag(K_inv)
    loo_var = 1.0 / np.diag(K_inv)
    loo_lpd = -0.5 * np.log(2 * np.pi * loo_var) - 0.5 * (y - loo_mean) ** 2 / loo_var

    return float(np.sum(loo_lpd))
```

### WAIC

Requires posterior samples. Run `gp.sample()` first, then compute WAIC from the resulting log-likelihoods.

### DIC

Uses the posterior mean deviance and deviance at the posterior mean. Simpler than WAIC but less robust for models with informative priors.

### When to Use Each

| Method | When to Use | Strengths |
|--------|------------|-----------|
| LOO-CV | Small datasets (n < 200) | No posterior samples needed for GPs |
| WAIC | Any size, have MCMC samples | Theoretically grounded, asymptotically equivalent to LOO |
| DIC | Quick screening | Simple to compute |
| BIC | Model selection among fixed models | Penalizes model complexity |
| AIC | Prediction-focused comparison | Optimistic but fast |

## Hyperparameter Sampling

The `TFPInterface.sample()` method runs Metropolis-Hastings in log-space on the GP hyperparameters:

```python
# Sample hyperparameter posteriors
gp = TFPInterface(model_config={"lengthscale": 1.0, "variance": 1.0, "noise": 0.01})
gp.create_spatial_gp_model(X_train, y_train)

traces = gp.sample(n_samples=5000, n_warmup=1000, seed=42, proposal_std=0.1)

# Inspect traces
for param in ["lengthscale", "variance", "noise"]:
    values = traces[param]
    print(f"{param}: mean={values.mean():.4f}, std={values.std():.4f}, "
          f"95% CI=[{np.percentile(values, 2.5):.4f}, {np.percentile(values, 97.5):.4f}]")
```

## Integration with Active Inference

GEO-INFER-BAYES provides posterior distributions that GEO-INFER-ACT uses for belief updating and policy selection.

### Workflow: Bayesian Spatial Model to Active Inference

```python
from geo_infer_bayes.api.tfp_interface import TFPInterface
from geo_infer_act.core.free_energy import FreeEnergyCalculator

# Step 1: Fit spatial GP
gp = TFPInterface(model_config={"lengthscale": 2.0, "variance": 1.0, "noise": 0.05})
gp.create_spatial_gp_model(sensor_locations, sensor_readings)

# Step 2: Predict at decision-relevant locations
candidate_locations = np.array([[5.0, 5.0], [3.0, 7.0], [8.0, 2.0]])
mu, var = gp_predict(gp, candidate_locations)

# Step 3: Convert GP posterior to beliefs for Active Inference
# Normalize predictions to probability-like distribution
beliefs = np.exp(-0.5 * (mu - mu.mean()) ** 2 / var.mean())
beliefs = beliefs / beliefs.sum()

# Step 4: Compute free energy for policy evaluation
fe_calc = FreeEnergyCalculator()
observations = np.array([0.5, 0.3, 0.2])  # current observation distribution
free_energy = fe_calc.compute_categorical_free_energy(
    beliefs=beliefs,
    observations=observations,
)

print(f"Policy free energy: {free_energy:.4f}")
# Lower free energy = better policy (less surprise)
```

The key integration point is converting GP posterior moments (mean and variance) into belief distributions that the Active Inference engine can reason about. Locations with high posterior variance represent high epistemic uncertainty -- Active Inference will prefer policies that reduce this uncertainty (epistemic foraging).

## See Also

- [Custom Models](advanced/custom_models.md) -- building custom Bayesian models
- [Active Inference Guide](active_inference_guide.md) -- Active Inference fundamentals
- [Performance Optimization](advanced/performance_optimization.md) -- optimizing GP computations
- [Temporal Analysis Guide](temporal_analysis_guide.md) -- time series methods
