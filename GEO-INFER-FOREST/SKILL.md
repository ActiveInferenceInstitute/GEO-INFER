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

- **Forest cover**: Change detection, canopy height models, NDVI analysis
- **Timber inventory**: Volume estimation, growth modeling, harvest planning
- **Deforestation**: Alert systems, historical trend analysis, driver attribution
- **Carbon stocks**: Above/below-ground biomass, soil organic carbon
- **Wildfire**: Risk mapping, fire spread modeling, post-fire recovery

### Key Imports

```python
from geo_infer_forest.core.cover_analysis import ForestCoverAnalyzer
from geo_infer_forest.core.carbon import CarbonStockEstimator
from geo_infer_forest.core.fire_risk import WildfireRiskModel
from geo_infer_forest.core.inventory import TimberInventory
```

## Examples

```python
from geo_infer_forest.core.cover_analysis import ForestCoverAnalyzer

analyzer = ForestCoverAnalyzer()
change = analyzer.detect_change(t1_raster, t2_raster)
loss_area_km2 = change.total_loss_area()
```

## Guidelines


### Integrations

- Integrates with BIO for forest biodiversity assessment
- Integrates with CLIMATE for climate-driven forest risk
- Integrates with SPACE for H3-based forest tessellation
- Test: `uv run python -m pytest GEO-INFER-FOREST/tests/ -v`
