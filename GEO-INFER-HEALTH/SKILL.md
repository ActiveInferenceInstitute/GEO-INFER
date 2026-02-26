---
name: geo-infer-health
description: Spatial epidemiology and public health analysis. Use when modeling disease spread, analyzing health disparities, performing spatial health risk assessment, building epidemiological surveillance systems, or assessing healthcare accessibility.
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

# GEO-INFER-HEALTH

## Instructions

### Core Capabilities

- **Spatial epidemiology**: Disease clustering (SaTScan), hotspot detection, SIR/SEIR spatial models
- **Health disparities**: Accessibility analysis, equity mapping, deprivation indices
- **Risk assessment**: Environmental health risk, exposure modeling
- **Surveillance**: Real-time epidemiological monitoring, early warning systems
- **Accessibility**: Hospital catchment areas, travel time to care, coverage gaps
- **Data validation**: Coordinate precision checks (flags >6 decimal places as suspect)

### Key Imports

```python
from geo_infer_health.core.epidemiology import EpidemiologicalModel
from geo_infer_health.core.risk_assessment import HealthRiskAssessor
from geo_infer_health.core.accessibility import HealthcareAccessAnalyzer
from geo_infer_health.utils.advanced_geospatial import SpatialValidator
```

## Examples

```python
from geo_infer_health.core.epidemiology import EpidemiologicalModel

model = EpidemiologicalModel(disease_type="infectious")
clusters = model.detect_clusters(cases_gdf, method="satscan")
risk_surface = model.compute_risk_surface(clusters, population_raster)
```

## Guidelines

- Coordinate validation checks for unrealistic precision (>6 decimal places)

### Integrations

- Integrates with SPACE for H3-based health district tessellation
- Integrates with TRANSPORT for healthcare accessibility travel times
- Test: `uv run python -m pytest GEO-INFER-HEALTH/tests/ -v`
