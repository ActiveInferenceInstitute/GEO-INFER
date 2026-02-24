---
title: "GEO-INFER-BIO: Biodiversity and Ecology"
description: "Species distribution, habitat analysis, and conservation planning"
purpose: "Enable biodiversity monitoring and ecological analysis"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-24"
dependencies: ["SPACE", "DATA", "TIME"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-DATA", "GEO-INFER-FOREST"]
tags: ["biodiversity", "ecology", "species", "habitat", "conservation"]
difficulty: "Intermediate"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a>
</div>

---

# GEO-INFER-BIO: Biodiversity and Ecology

## Overview

**GEO-INFER-BIO** provides ecological analysis:

- **Species Distribution**: SDM modeling
- **Habitat Analysis**: Quality, connectivity
- **Conservation Planning**: Prioritization
- **Biodiversity Metrics**: Diversity indices

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

print(f"Suitable habitat: {distribution.area_km2} km²")
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

## Methods

| Method | Application |
|--------|-------------|
| **MaxEnt** | Species distribution |
| **Marxan** | Conservation planning |
| **Circuitscape** | Connectivity |

## Installation

```bash
uv pip install -e "./GEO-INFER-BIO"
```

---

**Status**: Alpha

**Last Updated**: 2026-02-24
