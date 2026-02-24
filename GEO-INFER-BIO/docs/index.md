# GEO-INFER-BIO Documentation

## Welcome to GEO-INFER-BIO

This module provides biodiversity and ecological analysis capabilities for the GEO-INFER framework.

## Documentation Index

### Getting Started

- [README](../README.md) - Module overview and quick start
- [AGENTS](../AGENTS.md) - Agent capabilities

### Guides

- [Species Distribution Modeling](#species-distribution-modeling)
- [Habitat Analysis](#habitat-analysis)
- [Conservation Planning](#conservation-planning)
- [Biodiversity Metrics](#biodiversity-metrics)

## Species Distribution Modeling

### MaxEnt Models

```python
from geo_infer_bio import SpeciesModeler

modeler = SpeciesModeler(algorithm="maxent")

distribution = modeler.fit(
    occurrences=species_points,
    predictors=environmental_layers
)

suitability = modeler.predict(new_area)
```

## Habitat Analysis

### Connectivity

```python
from geo_infer_bio import HabitatAnalyzer

analyzer = HabitatAnalyzer()

connectivity = analyzer.analyze_connectivity(
    patches=habitat_patches,
    resistance=land_cover
)
```

## Conservation Planning

### Systematic Planning

```python
from geo_infer_bio import ConservationPlanner

planner = ConservationPlanner()

solution = planner.prioritize(
    targets=species_targets,
    cost=land_cost,
    budget=10_000_000
)
```

## Biodiversity Metrics

### Diversity Indices

| Index | Description |
|-------|-------------|
| Shannon | Entropy-based diversity |
| Simpson | Dominance measure |
| Species Richness | Species count |
| Evenness | Distribution equality |

---

**Last Updated**: 2026-02-24
