---
name: geo-infer-marine
description: Marine and ocean analysis for coastal and offshore environments. Use when analyzing ocean currents, marine ecosystems, coastal erosion, bathymetry, marine protected area planning, or fisheries management.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-bayes
    - geo-infer-time
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-MARINE

## Instructions

### Core Capabilities

- **Ocean currents**: Flow modeling, upwelling detection, Lagrangian transport
- **Marine ecosystems**: Habitat mapping, species distribution, coral reef health
- **Coastal analysis**: Erosion modeling, sea level rise impacts, storm surge
- **Bathymetry**: Seafloor mapping, depth analysis, substrate classification
- **MPA planning**: Marine protected area optimization, connectivity networks
- **Fisheries**: Stock assessment, spatial catch analysis, fleet dynamics

### Key Imports

```python
from geo_infer_marine.core.ocean import OceanCurrentModel
from geo_infer_marine.core.coastal import CoastalAnalyzer
from geo_infer_marine.core.mpa import MPAPlanner
from geo_infer_marine.core.fisheries import FisheriesModel
```

## Examples

```python
from geo_infer_marine.core.coastal import CoastalAnalyzer

analyzer = CoastalAnalyzer()
erosion_risk = analyzer.compute_erosion_risk(shoreline, wave_data)
slr_impact = analyzer.project_sea_level_rise(dem, scenario="RCP8.5")
```

## Guidelines


### Integrations

- Integrates with CLIMATE for ocean temperature projections
- Integrates with BIO for marine biodiversity assessment
- Test: `uv run python -m pytest GEO-INFER-MARINE/tests/ -v`
