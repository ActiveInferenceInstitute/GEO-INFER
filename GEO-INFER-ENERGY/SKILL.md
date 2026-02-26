---
name: geo-infer-energy
description: Energy systems analysis and renewable energy siting. Use when computing LCOE, analyzing energy grid spatial patterns, optimizing renewable energy placement, assessing energy storage, or performing techno-economic analysis of energy projects.
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

# GEO-INFER-ENERGY

## Instructions

### Core Capabilities

- **LCOE**: Levelized cost of energy calculations for solar, wind, hydro
- **Renewable siting**: Resource assessment, terrain analysis, constraint mapping
- **Grid analysis**: Spatial energy grid modeling, load flow, transmission losses
- **Techno-economics**: NPV, IRR, payback analysis for energy investments
- **Emissions**: Carbon intensity mapping, reduction pathway scenarios

### Key Imports

```python
from geo_infer_energy.core.lcoe import LCOECalculator
from geo_infer_energy.core.renewable_siting import RenewableSiteSelector
from geo_infer_energy.core.grid_analysis import GridAnalyzer
from geo_infer_energy.core.techno_economics import TechnoEconomicModel
```

## Examples

```python
from geo_infer_energy.core.renewable_siting import RenewableSiteSelector

selector = RenewableSiteSelector(technology="solar")
candidates = selector.evaluate(
    solar_irradiance=ghi_raster,
    terrain=dem,
    constraints={"slope_max": 15, "distance_from_grid_km": 10}
)
optimal_sites = selector.rank(candidates, n_top=5)
```

## Guidelines

- LCOE benchmarking in development (Alpha)

### Integrations

- Integrates with CLIMATE for renewable resource projections
- Integrates with SPACE for spatial optimization grid
- Test: `uv run python -m pytest GEO-INFER-ENERGY/tests/ -v`
