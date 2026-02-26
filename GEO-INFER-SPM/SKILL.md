---
name: geo-infer-spm
description: Statistical Parametric Mapping for geospatial data. Use when performing GLM-based spatial analysis, random field theory corrections, cluster-level inference, or neuroimaging-style statistical mapping on geographic datasets.
prerequisites:
  required:
    - geo-infer-act
    - geo-infer-bayes
  recommended:
    - geo-infer-space
    - geo-infer-time
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-SPM

## Instructions

### Core Capabilities

- **GLM fitting**: General linear models with spatial design matrices
- **Random field theory**: Multiple comparison correction for spatial data
- **Cluster inference**: Cluster-level and peak-level statistics
- **Contrast testing**: T-contrasts and F-contrasts on spatial maps
- **Visualization**: Interactive time series explorer (mean±SD + residuals)

### Key Imports

```python
from geo_infer_spm.core.glm import GLMModel
from geo_infer_spm.core.random_field import RandomFieldTheory
from geo_infer_spm.models.data_models import SPMData, SPMResult
from geo_infer_spm.visualization.interactive import create_time_series_explorer
```

## Examples

```python
from geo_infer_spm.models.data_models import SPMData
import numpy as np

data = SPMData(
    data=np.random.randn(100, 50),
    coordinates=np.column_stack([
        np.random.uniform(-90, 90, 100),   # latitudes
        np.random.uniform(-180, 180, 100)   # longitudes
    ])
)
```

## Guidelines

- Coordinates must be valid: latitude ∈ [-90, 90], longitude ∈ [-180, 180]
- GLM implementation is Alpha status — spatial design matrices in progress
- Time series explorer uses Plotly for interactive mean±SD visualization
- Test: `uv run python -m pytest GEO-INFER-SPM/tests/ -v`

### Integrations

- **MATH** → Spatial statistics and topology input
- **BAYES** → Bayesian GLM parameter estimation
- **SPACE** → Spatial residual fields from H3 grids
- **AI** → Feature engineering for statistical maps
