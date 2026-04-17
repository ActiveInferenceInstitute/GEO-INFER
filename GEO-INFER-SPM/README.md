---
title: "GEO-INFER-SPM: Statistical Parametric Mapping"
description: "SPM (GLM + Random Field Theory) for spatiotemporally continuous geospatial data"
purpose: "Rigorous statistical inference over continuous spatial/temporal fields"
module_type: "Core Analysis"
status: "Beta"
last_updated: "2026-04-16"
dependencies: ["SPACE", "MATH", "DATA", "BAYES"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-MATH", "GEO-INFER-DATA", "GEO-INFER-BAYES", "GEO-INFER-TIME"]
tags: ["statistics", "spm", "glm", "random-field-theory", "spatial-inference"]
difficulty: "Advanced"
estimated_time: "50"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> •
  <a href="../README.md#-module-overview">Module Index</a> •
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-SPM: Statistical Parametric Mapping

## Overview

**GEO-INFER-SPM** adapts Statistical Parametric Mapping — the standard inferential framework used in neuroimaging — to geospatial analysis. It fits voxel-wise General Linear Models over continuous spatial/temporal fields, applies Random Field Theory (RFT) for multiple-comparison correction, and supports cluster-based and Bayesian extensions. Design matrices, contrasts, and statistical maps use a consistent API from exploratory analysis through publication-quality output.

## Core Methodology

```text
Data field (SPMData) --> Design matrix --> GLM fit --> Contrast --> SPM + RFT correction
```

- **General Linear Model (GLM)**: voxel-wise regression on spatial/temporal grids
- **Random Field Theory**: family-wise error correction using smoothness estimates (FWHM)
- **Cluster inference**: extent- and mass-based thresholding on smoothness-corrected fields
- **Bayesian SPM**: hierarchical priors with posterior probability maps
- **Mixed-effects**: subject/group-level modeling for panel data
- **Nonparametric SPM**: permutation testing for small-sample and non-Gaussian fields

## Features

### Fit a GLM and Compute a Contrast Map

```python
import geo_infer_spm as gispm

data = gispm.load_data("temperature_grid.tif")
design = gispm.create_design_matrix(
    factors=[("season", ["winter", "spring"])],
    covariates={"elevation": elevation_array},
)

model = gispm.fit_glm(data, design)
contrast = gispm.contrast(model, "spring > winter")
spm_map = gispm.compute_spm(model, contrast, correction="RFT")

gispm.visualize_spm(spm_map, threshold="FWE_0.05")
```

### Spatial Regression (Lag / Error)

```python
from geo_infer_spm import fit_spatial_model

result = fit_spatial_model(
    y=housing_prices,
    X=predictors,
    weights=spatial_weights,   # libpysal weights matrix
    model_type="spatial_lag",  # or "spatial_error", "gwr"
)
print(result.rho, result.r_squared, result.aic)
```

### Mixed-Effects SPM

```python
from geo_infer_spm import fit_mixed_effects

result = fit_mixed_effects(
    data=panel_data,
    fixed_effects=["treatment", "covariate"],
    random_effects={"subject": ["intercept", "slope"]},
)
```

### Nonparametric (Permutation) SPM

```python
from geo_infer_spm import fit_nonparametric

result = fit_nonparametric(
    data=data,
    design=design,
    contrast=contrast,
    n_permutations=5000,
    cluster_threshold=3.1,
)
```

### Bayesian SPM

```python
from geo_infer_spm import BayesianSPM

bspm = BayesianSPM(prior="hierarchical_gaussian")
posterior_map = bspm.fit(data, design, contrast)
ppm = bspm.posterior_probability_map(threshold=0.0)
```

## API Reference

| Function / Class | Purpose |
|------------------|---------|
| `fit_glm(data, design)` → `GeneralLinearModel` | Voxel-wise GLM fit |
| `contrast(model, specification)` → `Contrast` | Build a contrast vector from symbolic spec |
| `compute_spm(model, contrast, correction)` → `SPMResult` | Statistical parametric map with FWE/FDR/cluster correction |
| `RandomFieldTheory(fwhm, dim)` | RFT-based threshold computation |
| `fit_spatial_model(y, X, weights, model_type)` | Spatial lag / error / GWR |
| `fit_mixed_effects(data, fixed, random)` | Linear mixed-effects over spatial fields |
| `fit_nonparametric(...)` | Permutation-based SPM inference |
| `BayesianSPM(prior, ...)` | Bayesian extension with posterior probability maps |
| `SpatialAnalyzer(...)` | High-level spatial SPM helper (autocorr, clustering) |
| `TemporalAnalyzer(...)` | Temporal SPM for time-series fields |
| `ModelValidator(...)` | Residual autocorrelation, effective df, smoothness checks |
| `create_design_matrix(factors, covariates)` | Factor/covariate design matrix builder |
| `generate_synthetic_data(...)` | Simulated SPM data for testing/tutorials |
| `visualize_spm(map, threshold, ...)` | Threshold-and-render statistical map |
| `SPMAPI` | FastAPI service for remote SPM jobs |

## Data Models

| Model | Purpose |
|-------|---------|
| `SPMData` | Spatial/temporal field with CRS and metadata |
| `SPMResult` | Fitted SPM with statistics, thresholds, clusters |
| `ContrastResult` | Contrast-specific results (effect size, t/F, p-values) |

## Methods Available

| Method | Application |
|--------|-------------|
| GLM (voxel-wise) | Regression across spatial/temporal fields |
| RFT correction | Family-wise error control on smooth fields |
| Cluster-extent / mass | Topological inference |
| Spatial lag / error | Areal data with spatial autocorrelation |
| GWR | Local (geographically-weighted) regression |
| Mixed-effects | Multi-level / panel designs |
| Permutation | Nonparametric cluster inference |
| Bayesian SPM | Posterior probability maps |

## Integration

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-MATH** | SPM ← MATH | Linear algebra, smoothing kernels, RFT Euler characteristic |
| **GEO-INFER-SPACE** | SPM ← SPACE | H3 indexing, spatial weights matrices |
| **GEO-INFER-DATA** | SPM ← DATA | Raster/vector data loading and alignment |
| **GEO-INFER-BAYES** | SPM ↔ BAYES | Hierarchical priors for Bayesian SPM |
| **GEO-INFER-TIME** | SPM ↔ TIME | Temporal designs and time-series fields |

## Installation

```bash
uv pip install -e "./GEO-INFER-SPM"

# Optional extras
uv pip install -e "./GEO-INFER-SPM[bayes]"      # pymc / arviz
uv pip install -e "./GEO-INFER-SPM[spatial]"    # libpysal, mgwr
```

## Testing

```bash
uv run python -m pytest GEO-INFER-SPM/tests/ -v
uv run python -m pytest GEO-INFER-SPM/tests/ --cov=GEO-INFER-SPM/src --cov-report=html
```

## Documentation Hub

Full framework documentation is in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation and quick-start |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | Cross-module workflows |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards |

---

**Status**: Beta

**Last Updated**: 2026-04-16
