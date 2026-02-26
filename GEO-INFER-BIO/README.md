---
title: "GEO-INFER-BIO: Biodiversity and Ecology"
description: "Species distribution, habitat analysis, and conservation planning"
purpose: "Enable biodiversity monitoring and ecological analysis"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "DATA", "TIME"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-DATA", "GEO-INFER-FOREST"]
tags: ["biodiversity", "ecology", "species", "habitat", "conservation"]
difficulty: "Intermediate"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> |
  <a href="../README.md#-module-overview">Module Index</a> |
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-BIO: Biodiversity and Ecology

## Overview

**GEO-INFER-BIO** provides biodiversity analysis, species distribution modeling (SDM), habitat quality assessment, ecological connectivity analysis, and conservation planning tools. The module supports the full workflow from species occurrence records through spatial biodiversity mapping to corridor identification and protected area prioritization. It operates on H3 hexagonal grids for consistent spatial aggregation and integrates with Bayesian methods for uncertainty-aware species distribution predictions.

## Core Objectives

- **Species Richness Mapping**: Aggregate species occurrence records onto H3 hexagonal cells to produce spatially explicit richness maps with rarefaction-corrected estimates
- **Habitat Connectivity Analysis**: Identify viable wildlife corridors between habitat patches using graph-theoretic methods (least-cost paths, circuit theory) with species-specific dispersal parameters
- **Bayesian Species Distribution Modeling**: Predict species occurrence probability across unsampled areas using environmental covariates and Bayesian inference (via GEO-INFER-BAYES)
- **Conservation Prioritization**: Rank candidate areas for protection using systematic conservation planning methods that balance biodiversity value, cost, and connectivity

## Features

### Species Distribution Modeling

```python
from geo_infer_bio import SpeciesModeler

# Model species distribution
modeler = SpeciesModeler()

distribution = modeler.predict(
    species="ursus_americanus",
    occurrences=sighting_data,
    predictors=environmental_layers
)

print(f"Suitable habitat: {distribution.area_km2} km2")
```

### Habitat Analysis

```python
from geo_infer_bio import HabitatAnalyzer

# Analyze habitat
analyzer = HabitatAnalyzer()

quality = analyzer.assess(
    area=study_region,
    metrics=["connectivity", "fragmentation"]
)
```

### Conservation Planning

```python
from geo_infer_bio import ConservationPlanner

# Prioritize conservation
planner = ConservationPlanner()

plan = planner.prioritize(
    targets=species_targets,
    cost=land_costs
)
```

### Biodiversity Metrics

```python
from geo_infer_bio import BiodiversityCalculator

# Calculate diversity
calc = BiodiversityCalculator()

metrics = calc.compute(
    data=survey_data,
    indices=["shannon", "simpson"]
)
```

## API Reference

| Class / Function | Description |
|------------------|-------------|
| `BiodiversityAnalyzer(h3_resolution)` | Primary analyzer for spatial biodiversity metrics on H3 grids |
| `SpeciesDistributionModel(method, covariates)` | SDM with MaxEnt, GLM, or Bayesian methods |
| `HabitatConnectivityAnalyzer()` | Graph-based corridor detection between habitat patches |
| `BiodiversityAnalyzer.compute_species_richness(occurrences)` | Returns H3-aggregated species richness GeoDataFrame |
| `HabitatConnectivityAnalyzer.find_corridors(patches, species_requirements)` | Returns GeoDataFrame of viable corridors with cost-distance values |
| `SpeciesDistributionModel.fit(occurrences, environment)` | Fits SDM to occurrence and environmental data |
| `SpeciesDistributionModel.predict(grid)` | Returns occurrence probability predictions across a spatial grid |
| `BiodiversityAnalyzer.shannon_index(counts)` | Computes Shannon diversity index from species abundance counts |

## Methods

| Method | Application |
|--------|-------------|
| **MaxEnt** | Species distribution |
| **Marxan** | Conservation planning |
| **Circuitscape** | Connectivity |

## Working Code Examples

### Example 1: Species Richness Estimation

```python
from geo_infer_bio.core.biodiversity_analyzer import BiodiversityAnalyzer
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

# Species occurrence records
np.random.seed(42)
n_records = 60
species_list = ["Quercus robur", "Fagus sylvatica", "Pinus sylvestris"] * 20
lats = 47.5 + np.random.uniform(0, 0.5, n_records)
lngs = -122.5 + np.random.uniform(0, 0.5, n_records)

occurrences = gpd.GeoDataFrame(
    {"species": species_list},
    geometry=[Point(lng, lat) for lat, lng in zip(lats, lngs)],
    crs="EPSG:4326",
)

analyzer = BiodiversityAnalyzer(h3_resolution=8)
richness_map = analyzer.compute_species_richness(occurrences)
print(f"Max species richness: {richness_map['richness'].max()} species")
```

### Example 2: Habitat Connectivity Analysis

```python
from geo_infer_bio.core.connectivity_analyzer import HabitatConnectivityAnalyzer
import geopandas as gpd

analyzer = HabitatConnectivityAnalyzer()
habitat_patches = gpd.read_file("habitat_polygons.geojson")
corridors = analyzer.find_corridors(
    patches=habitat_patches,
    species_requirements={"min_area_ha": 5.0, "max_gap_km": 2.0},
)
print(f"Found {len(corridors)} viable wildlife corridors")
```

## Integration

GEO-INFER-BIO integrates with the following modules:

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-SPACE** | BIO <-- SPACE | H3 grid operations for spatial biodiversity aggregation |
| **GEO-INFER-DATA** | BIO <-- DATA | Species occurrence datasets and environmental raster layers |
| **GEO-INFER-BAYES** | BIO <-- BAYES | Bayesian inference for uncertainty-aware species distribution models |
| **GEO-INFER-FOREST** | BIO <-> FOREST | Forest habitat structure informs biodiversity; biodiversity metrics guide forestry decisions |
| **GEO-INFER-MARINE** | BIO <-> MARINE | Marine biodiversity assessments and coastal habitat connectivity |
| **GEO-INFER-CLIMATE** | BIO <-- CLIMATE | Climate variables as environmental covariates for SDMs |

Data flow: DATA provides occurrence records and environmental layers. SPACE provides H3 spatial operations. BAYES powers uncertainty quantification in SDMs. BIO produces richness maps, corridors, and conservation priorities that feed into FOREST and MARINE for domain-specific management.

## Installation

```bash
uv pip install -e "./GEO-INFER-BIO"
```

## Testing

```bash
# Run all BIO tests
uv run python -m pytest GEO-INFER-BIO/tests/ -v

# Run unit tests only
uv run python -m pytest GEO-INFER-BIO/tests/unit/ -v

# Run with coverage
uv run python -m pytest GEO-INFER-BIO/tests/ --cov=GEO-INFER-BIO/src --cov-report=html
```

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |

---

**Status**: Alpha

**Last Updated**: 2026-02-25
