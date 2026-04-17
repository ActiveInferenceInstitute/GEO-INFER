# GEO-INFER-MATH: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> •
  <a href="../README.md#-module-overview">Module Index</a> •
  <a href="./README.md">Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-MATH** module is the mathematical foundation of the framework. It provides agents with spatial statistics, interpolation, optimization, geometry, linear algebra, graph theory, information theory, and coordinate transforms. All APIs are direct-callable and have no dependencies on other GEO-INFER modules.

## Agent Capabilities

### 1. Spatial Statistics

```python
from geo_infer_math import MoranI, ripley_k, semivariogram

moran = MoranI()
I, p_value = moran.compute(values=y, weights=W)
K, r = ripley_k(points=xy, area=total_area, r_values=np.linspace(0, 1000, 20))
h, gamma = semivariogram(points=xy, values=y, n_lags=15)
```

### 2. Interpolation

```python
from geo_infer_math import (
    InterpolationManager, IDWInterpolator, KrigingInterpolator, RBFInterpolator
)

# Direct use
idw = IDWInterpolator(power=2)
idw.fit(xy, values)
grid = idw.predict(prediction_xy)

# Manager with backend dispatch
mgr = InterpolationManager(config={"method": "kriging"})
surface = mgr.interpolate(points=xy, values=values, grid=prediction_grid)
```

### 3. Optimization

```python
from geo_infer_math import (
    OptimizationManager, ScipyOptimizer, GeneticAlgorithmOptimizer,
    MultiObjectiveOptimizer, compare_optimization_methods,
)

opt = ScipyOptimizer()
result = opt.minimize(fn=objective, x0=x0, bounds=bounds)
print(result.x, result.fun, result.converged)

# Compare methods
comparison = compare_optimization_methods(
    fn=objective,
    x0=x0,
    methods=["scipy", "ga", "gradient_descent"],
)
```

### 4. Geometry & Coordinate Transforms

```python
from geo_infer_math import (
    Point, haversine_distance, vincenty_distance,
    bearing, destination_point, polygon_area_spherical,
)
from geo_infer_math.core.transforms import CoordinateTransformer

d_km = haversine_distance(lat1=37.7, lon1=-122.4, lat2=40.7, lon2=-74.0) / 1000
b_deg = bearing(37.7, -122.4, 40.7, -74.0)

xf = CoordinateTransformer(source_crs="EPSG:4326", target_crs="EPSG:3857")
xy_proj = xf.transform(xy_lonlat)
```

### 5. Linear Algebra / Tensors

```python
from geo_infer_math.core.linalg_tensor import (
    MatrixOperations, TensorOperations, SpatialLinearAlgebra,
)

mo = MatrixOperations()
W = mo.spatial_weights_matrix(geometries, method="queen")
eigvals, eigvecs = mo.eigendecompose(W)
```

### 6. Graph Theory

```python
from geo_infer_math import SpatialGraph, NetworkFlow

G = SpatialGraph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)
path = G.shortest_path(source=1, target=10, weight="distance")

flow = NetworkFlow(G)
max_flow = flow.max_flow(source=1, sink=10, capacity="capacity")
```

### 7. Information Theory

```python
from geo_infer_math import shannon_entropy, mutual_information, kl_divergence

H = shannon_entropy(probabilities)
I = mutual_information(x, y)
D = kl_divergence(p, q)
```

### 8. Convenience Bridges (Optional)

```python
from geo_infer_math.api.convenience import (
    ActiveInferenceConvenience, BayesianConvenience, SpatialConvenience,
)

act = ActiveInferenceConvenience()
F = act.free_energy(posterior, prior, likelihood)

bayes = BayesianConvenience()
posterior = bayes.update(prior, likelihood, evidence)
```

## Implementation Status

| Capability | Status | Notes |
|-----------|--------|-------|
| Spatial statistics | Ready | Moran's I, Getis-Ord, Ripley K, semivariogram, LISA |
| Interpolation | Ready | IDW, Kriging, RBF, Linear, Cubic + manager |
| Optimization | Ready | Gradient descent, GA, scipy, multi-objective |
| Geometry | Ready | Great-circle distance, bearing, spherical area |
| Coordinate transforms | Ready | CRS transforms, UTM, affine, datum shifts |
| Linear algebra / tensors | Ready | Matrix/tensor ops, spatial linear algebra |
| Graph theory | Ready | SpatialGraph, NetworkFlow |
| Information theory | Optional | Shannon/Rényi/Tsallis entropy, MI, KL |
| Theorem proving | Optional | Bound checks, symbolic validation |
| Integration bridges | Optional | AI, ACT, BAYES convenience wrappers |

## Integration

| Consumer module | How MATH is used |
|-----------------|------------------|
| BAYES | Linear algebra, Cholesky, kernel matrices |
| ACT | Free energy math, variational helpers |
| AI | Loss functions, gradient bridges |
| SPACE | Distance metrics, weights matrices |
| SPM | GLM linear algebra, smoothness/RFT math |
| TIME | Numerical integration, root finding |

MATH has **no dependencies on other GEO-INFER modules** — it is a foundation that other modules build on.

---

**Last Updated**: 2026-04-16

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
