---
name: geo-infer-climate
description: Climate modeling and environmental analysis. Use when analyzing climate data, projecting future climate scenarios (RCP/SSP), computing climate indices (SPI, PDSI), performing statistical downscaling, or assessing climate change impacts on geographic regions.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-time
  recommended:
    - geo-infer-bayes
    - geo-infer-data
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-CLIMATE

## Instructions

### Core Capabilities

- **Climate projections**: RCP/SSP scenario modeling with ensemble methods
- **Climate indices**: SPI, PDSI, heat wave indices, frost days, growing degree days
- **Downscaling**: Statistical (bias correction, delta method) and dynamical downscaling
- **Impact assessment**: Sector-specific climate vulnerability and adaptation planning
- **Data integration**: CMIP6, ERA5, observational station networks, gridded datasets

### Key Imports

```python
from geo_infer_climate.core.projections import ClimateProjection
from geo_infer_climate.core.indices import ClimateIndexCalculator
from geo_infer_climate.core.downscaling import StatisticalDownscaler
from geo_infer_climate.core.impact import ImpactAssessment
```

## Examples

```python
from geo_infer_climate.core.indices import ClimateIndexCalculator

calculator = ClimateIndexCalculator()
spi = calculator.compute_spi(precipitation_series, scale=3)
pdsi = calculator.compute_pdsi(precip, temp, latitude)
```

## Guidelines


### Integrations

- Integrates with WATER for hydrological climate impacts
- Integrates with AG for agricultural climate adaptation
- Integrates with ENERGY for renewable resource projections
- Test: `uv run python -m pytest GEO-INFER-CLIMATE/tests/ -v`
