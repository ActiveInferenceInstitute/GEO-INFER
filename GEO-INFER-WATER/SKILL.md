---
name: geo-infer-water
description: Water resource management and hydrological modeling. Use when analyzing watersheds (D8 delineation, flow accumulation), water quality (WQI, pollution tracking, regulatory compliance), rainfall-runoff, water balance, flood/drought screening, or water supply allocation.
difficulty: intermediate
estimated_time: 45min
---

# GEO-INFER-WATER

## Instructions

### Core Capabilities

- **Watershed delineation**: D8 flow direction, topological-sort flow accumulation, upstream basin tracing, stream network extraction, slope calculation, and a full delineation pipeline
- **Water quality**: WQI calculation, pollution hotspot identification (with optional D8 upstream tracing), advection-diffusion plume tracking, trend analysis, risk assessment, regulatory compliance (EPA/WHO/EU), pollutant load estimation
- **Hydrology**: Rainfall-runoff split (mass-conserving, soil-moisture adjusted), groundwater recharge estimate, water balance (delegates to WaterBalanceModeler)
- **Water balance**: Thornthwaite and Hargreaves PET, SCS Curve Number runoff, monthly soil-moisture accounting, canonical water-balance closure
- **Flood & drought**: Equal-weight composite flood-risk screening (extreme precipitation + low elevation + optional soil saturation); drought risk from precipitation deficit
- **Infrastructure**: Priority-weighted water allocation (supply split by demand × priority, capped at demand, surplus redistributed) and capacity-gap assessment

Not implemented: Green-Ampt infiltration, aquifer/well-drawdown modeling, flood-frequency (return-period) analysis, inundation mapping. Groundwater is limited to a trivial recharge estimate.

### Key Imports

```python
from geo_infer_water import (
    HydrologicalModeler,
    WaterBalanceModeler,
    WaterQualityAssessor,
    WaterInfrastructurePlanner,
    FloodDroughtAnalyzer,
    WatershedDelineator,
)
```

## Examples

```python
import numpy as np
import xarray as xr
from geo_infer_water import HydrologicalModeler, WatershedDelineator, WaterQualityAssessor

# Rainfall-runoff (mass-conserving: runoff + infiltration == precipitation)
hydro = HydrologicalModeler()
precip = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
result = hydro.rainfall_runoff_model(precip, infiltration_rate=0.6)

# Watershed delineation (D8 flow direction + accumulation)
delineator = WatershedDelineator()
dem = xr.DataArray(np.array([[9, 8, 7], [8, 3, 5], [7, 5, 3]], dtype=float), dims=("y", "x"))
watershed = delineator.full_delineation(dem, outlet=(2, 2), cell_size=500.0)

# Water quality index
assessor = WaterQualityAssessor()
from geo_infer_water import WaterSample
sample = WaterSample("s1", (0.0, 0.0), "2024-07-15", ph=7.2, dissolved_oxygen=8.5,
                     turbidity=2.0, temperature=18.0, nitrate=2.0, e_coli=10)
wqi = assessor.calculate_wqi(sample)
```

## Guidelines

- `WatershedDelineator` is the canonical watershed module; the older `WatershedAnalyzer` has been removed.
- `rainfall_runoff_model` conserves mass: `runoff + infiltration == precipitation` for any soil moisture.
- `HydrologicalModeler.calculate_water_balance` delegates to `WaterBalanceModeler.water_balance_closure` (single water-balance owner).
- `assess_flood_risk` is an equal-weight screening heuristic, not a calibrated flood model.
- `optimize_water_allocation` splits scarce supply by `demand * priority`, capped at each demand.

### Integrations

- Integrates with CLIMATE for precipitation projections
- Integrates with AG for irrigation water demand
- Test: `uv run python -m pytest GEO-INFER-WATER/tests/ -v`
