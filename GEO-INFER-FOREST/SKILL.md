---
name: geo-infer-forest
description: Forest analysis and forestry management. Use when analyzing forest cover change, timber inventory, deforestation detection, forest carbon stocks, wildfire risk assessment, or canopy structure analysis.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-bayes
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-FOREST

## Instructions

### Core Capabilities

- **Forest cover**: Change detection, NDVI/EVI analysis, canopy cover, LAI, gap detection
- **Timber inventory**: `ForestInventory` provides biomass estimation and forest area calculation.
- **Deforestation**: Alert systems, historical trend analysis, driver attribution
- **Carbon stocks**: Above/below-ground biomass, soil organic carbon
- **Wildfire**: Risk mapping, fire spread modeling, post-fire recovery

### Key Imports

```python
from geo_infer_forest import (
    CanopyAnalyzer,
    CarbonSequestrationModeler,
    DeforestationDetector,
    FireRiskAssessor,
    ForestInventory,
    WildfireRiskAnalyzer,
)
```

## Examples

```python

import numpy as np
import xarray as xr

from geo_infer_forest import CanopyAnalyzer, ForestInventory

analyzer = CanopyAnalyzer()
ndvi = analyzer.calculate_ndvi(
    red=xr.DataArray(np.full((4, 4), 0.05), dims=("y", "x")),
    nir=xr.DataArray(np.full((4, 4), 0.45), dims=("y", "x")),
)

inventory = ForestInventory()
biomass = inventory.estimate_biomass(
    forest_cover=xr.DataArray(np.full((4, 4), 70.0), dims=("y", "x"))
)
```

## Guidelines


### Integrations

- Integrates with BIO for forest biodiversity assessment
- Integrates with CLIMATE for climate-driven forest risk
- Integrates with SPACE for H3-based forest tessellation
- Test: `uv run python -m pytest GEO-INFER-FOREST/tests/ -v`
