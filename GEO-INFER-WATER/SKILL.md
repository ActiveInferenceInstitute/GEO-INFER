---
name: geo-infer-water
description: Water resource management and hydrological modeling. Use when analyzing watersheds, water quality, hydrological networks, groundwater systems, water supply/demand planning, or flood risk assessment.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-time
    - geo-infer-bayes
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-WATER

## Instructions

### Core Capabilities

- **Watershed analysis**: Delineation, flow accumulation, drainage networks
- **Water quality**: Pollutant transport, WQI (water quality index), turbidity modeling
- **Hydrology**: Rainfall-runoff (SCS-CN, Green-Ampt), flood frequency analysis
- **Groundwater**: Aquifer modeling, well drawdown, recharge estimation
- **Supply planning**: Water demand forecasting, infrastructure gap analysis
- **Flood risk**: Return period mapping, inundation modeling

### Key Imports

```python
from geo_infer_water.core.watershed import WatershedAnalyzer
from geo_infer_water.core.quality import WaterQualityModel
from geo_infer_water.core.hydrology import HydrologicalModel
from geo_infer_water.core.flood import FloodRiskAnalyzer
```

## Examples

```python
from geo_infer_water.core.watershed import WatershedAnalyzer

analyzer = WatershedAnalyzer(dem_raster)
basins = analyzer.delineate_basins(pour_points)
flow = analyzer.compute_flow_accumulation()
```

## Guidelines


### Integrations

- Integrates with CLIMATE for precipitation projections
- Integrates with AG for irrigation water demand
- Test: `uv run python -m pytest GEO-INFER-WATER/tests/ -v`
