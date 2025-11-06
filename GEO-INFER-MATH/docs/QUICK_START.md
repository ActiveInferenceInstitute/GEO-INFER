# GEO-INFER-MATH Quick Start Guide

## New Features Overview

### 1. Information Theory

```python
from geo_infer_math import (
    shannon_entropy,
    spatial_entropy,
    mutual_information,
    kl_divergence,
    EntropyCalculator
)

# Calculate spatial entropy
coordinates = np.random.rand(100, 2) * 100
values = np.random.rand(100)
entropy = spatial_entropy(coordinates, values)
print(f"Spatial entropy: {entropy:.4f}")

# Use calculator for multiple operations
calc = EntropyCalculator()
entropy = calc.calculate(values, method='shannon')
```

### 2. Theorem Proving

```python
from geo_infer_math import TheoremProver, create_prover

# Create theorem prover
prover = create_prover(backend='z3')

# Prove a theorem
result = prover.prove("For all x: x + 0 = x")
print(f"Status: {result.status}")
print(f"Proof: {result.proof}")
```

### 3. Convenience APIs

```python
from geo_infer_math import (
    ActiveInferenceConvenience,
    BayesianConvenience,
    AIConvenience
)

# Active Inference
act_conv = ActiveInferenceConvenience()
free_energy = act_conv.calculate_free_energy(observations, beliefs)

# Bayesian
bayes_conv = BayesianConvenience()
posterior = bayes_conv.calculate_posterior(prior, likelihood, data)

# AI/ML
ai_conv = AIConvenience()
gradient = ai_conv.compute_gradient(objective_function, parameters)
```

### 4. Module Integration

```python
from geo_infer_math.integration.act import FreeEnergyCalculator
from geo_infer_math.integration.bayes import PosteriorHelpers
from geo_infer_math.integration.ai import AIGradientHelpers

# Deep integration with other modules
fe_calc = FreeEnergyCalculator()
free_energy = fe_calc.calculate(observations, beliefs)
```

### 5. Configuration

```python
from geo_infer_math.config import configure, get_config

# Configure module
configure(
    theorem_proving_backend='z3',
    enable_caching=True,
    parallel_processing=True
)

# Get configuration
config = get_config()
timeout = config.get('theorem_proving', 'timeout')
```

### 6. Caching and Performance

```python
from geo_infer_math.utils.caching import cache_result, ComputationCache

# Cache expensive computations
@cache_result(maxsize=128)
def expensive_entropy_calculation(data):
    return shannon_entropy(data)

# Use cache manager
cache = ComputationCache(maxsize=256)
cached_result = cache.get('key')
if cached_result is None:
    result = expensive_computation()
    cache.set('key', result)
```

### 7. Validation

```python
from geo_infer_math.utils.validation import (
    validate_probabilities,
    validate_coordinates
)

@validate_probabilities
def calculate_entropy(probabilities):
    return shannon_entropy(probabilities)

@validate_coordinates
def spatial_analysis(coordinates, values):
    return spatial_entropy(coordinates, values)
```

## Migration Guide

### Using New Convenience APIs

**Before:**
```python
from geo_infer_math.core.spatial_statistics import MoranI
from geo_infer_math.core.linalg_tensor import MatrixOperations

# Manual setup
weights = MatrixOperations.spatial_weights_matrix(coords)
moran = MoranI(weights)
result = moran.compute(values, coords)
```

**After:**
```python
from geo_infer_math import SpatialConvenience

# Convenience API
conv = SpatialConvenience()
results = conv.comprehensive_analysis(coordinates, values)
```

### Using Information Theory

**New:**
```python
from geo_infer_math import (
    spatial_entropy,
    mutual_information,
    kl_divergence
)

# Direct function calls
entropy = spatial_entropy(coords, values)
mi = mutual_information(prob_xy, prob_x, prob_y)
kl = kl_divergence(dist_p, dist_q)
```

### Using Theorem Proving

**New:**
```python
from geo_infer_math import TheoremProver

prover = TheoremProver(backend='z3')
result = prover.prove("theorem_statement", assumptions=["assumption1"])
if result.status.value == 'proven':
    print("Theorem proven!")
```

## Best Practices

1. **Use Convenience APIs** for common operations
2. **Enable Caching** for repeated computations
3. **Use Validation** decorators for input safety
4. **Configure** module settings for your use case
5. **Use Integration Layers** for cross-module operations

## Performance Tips

1. Enable caching for expensive operations
2. Use parallel processing for batch operations
3. Cache theorem proving results
4. Use appropriate numerical precision
5. Validate inputs early to avoid wasted computation

