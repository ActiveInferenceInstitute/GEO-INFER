---
title: "GEO-INFER-SPM: Statistical Parametric Mapping"
description: "Spatial statistics, parametric mapping, and geostatistics"
purpose: "Provide advanced statistical analysis for geospatial data"
module_type: "Core Analysis"
status: "Beta"
last_updated: "2026-02-25"
dependencies: ["SPACE", "MATH", "DATA"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-MATH", "GEO-INFER-DATA"]
tags: ["statistics", "geostatistics", "analysis", "hypothesis-testing", "kriging"]
difficulty: "Advanced"
estimated_time: "50"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-SPM: Statistical Parametric Mapping

## Overview

**GEO-INFER-SPM** provides spatial statistics capabilities:

- **Parametric Mapping**: Statistical significance maps
- **Spatial Regression**: Lag and error models
- **Geostatistics**: Variograms, kriging, interpolation
- **Hypothesis Testing**: Spatial pattern tests

## Features

### Parametric Mapping

```python
from geo_infer_spm import ParametricMapper

# Create significance maps
mapper = ParametricMapper()

result = mapper.analyze(
    data=population_density,
    hypothesis="hotspot_detection",
    significance=0.05
)

print(f"Significant clusters: {result.clusters}")
```

### Spatial Regression

```python
from geo_infer_spm import SpatialRegressor

# Fit spatial model
regressor = SpatialRegressor()

model = regressor.fit(
    y=housing_prices,
    X=predictors,
    spatial_weights=weights,
    model_type="spatial_lag"
)

print(f"R-squared: {model.r_squared}")
```

### Geostatistics

```python
from geo_infer_spm import Geostatistics

# Kriging interpolation
geo = Geostatistics()

variogram = geo.compute_variogram(
    data=samples,
    model="spherical"
)

interpolated = geo.krige(
    data=samples,
    variogram=variogram,
    grid=prediction_grid
)
```

### Hypothesis Testing

```python
from geo_infer_spm import SpatialTester

# Test for clustering
tester = SpatialTester()

result = tester.test(
    points=crime_locations,
    null="random",
    test="ripley_k"
)

print(f"Clustering: {result.is_significant}")
```

## Methods

| Method | Application |
|--------|-------------|
| **Moran's I** | Autocorrelation |
| **LISA** | Local indicators |
| **Kriging** | Interpolation |
| **GWR** | Local regression |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-MATH** | Computation |
| **GEO-INFER-DATA** | Data sources |

## Installation

```bash
uv pip install -e "./GEO-INFER-SPM"
```

---

**Status**: Beta

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
