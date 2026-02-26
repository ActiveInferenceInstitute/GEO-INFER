---
name: geo-infer-ag
description: Precision agriculture and soil health modeling. Use when analyzing soil health, crop water usage (FAO-56), carbon sequestration (IPCC Tier 1), precision farming, or agricultural land management.
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

# GEO-INFER-AG

## Instructions

### Core Capabilities

- **Soil health**: USDA soil data integration, nutrient modeling
- **Carbon sequestration**: IPCC Tier 1 methodology for agricultural carbon
- **Water usage**: FAO-56 crop-specific water productivity calculations
- **Precision farming**: Variable rate application, yield prediction
- **Land management**: Crop rotation optimization, field boundary analysis

### Key Imports

```python
from geo_infer_ag.models.soil_health import SoilHealthModel
from geo_infer_ag.models.carbon_sequestration import CarbonSequestrationModel
from geo_infer_ag.models.water_usage import WaterUsageModel
```

## Examples

```python
from geo_infer_ag.models.water_usage import WaterUsageModel

model = WaterUsageModel(crop="maize", climate_zone="temperate")
daily_water = model.compute_daily_requirement(
    eto=5.2,  # reference evapotranspiration (mm/day)
    growth_stage="mid_season"
)
print(f"Crop water need: {daily_water:.1f} mm/day")
seasonal = model.seasonal_demand(planting_date="2026-04-15")
```

```python
from geo_infer_ag.models.carbon_sequestration import CarbonSequestrationModel

carbon = CarbonSequestrationModel(method="ipcc_tier1")
result = carbon.estimate(
    land_area_ha=100,
    soil_type="clay_loam",
    management="no_till"
)
print(f"Annual sequestration: {result.tonnes_co2_per_year:.1f} t CO₂/yr")
```

## Guidelines

- Soil models use USDA data (not random values)
- Carbon uses IPCC Tier 1 methodology
- Water productivity uses FAO-56 crop-specific defaults
- Test: `uv run python -m pytest GEO-INFER-AG/tests/ -v`

### Integrations

- **CLIMATE** → Precipitation projections for irrigation planning
- **WATER** → Irrigation water demand modeling
- **SPACE** → H3-based field tessellation and precision farming grids
- **RISK** → Crop loss risk assessment
- **ECON** → Agricultural market pricing and supply chain
