# GEO-INFER-BIO: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-BIO** module provides biodiversity and ecological capabilities for agents, including species distribution modeling, habitat analysis, and conservation planning.

## Agent Capabilities

### 1. Species Distribution

```python
from geo_infer_bio import SpeciesModeler

# Model species distribution
modeler = SpeciesModeler()

distribution = modeler.predict(
    species="ursus_americanus",
    occurrences=sighting_data,
    predictors=environmental_layers)

print(f"Suitable habitat: {distribution.area_km2} km²")```

### 2. Habitat Analysis

```python
from geo_infer_bio import HabitatAnalyzer

# Analyze habitat quality
analyzer = HabitatAnalyzer()

quality = analyzer.assess(
    area=study_region,
    metrics=["connectivity", "fragmentation", "core_area"])

print(f"Habitat quality: {quality.score}")```

### 3. Conservation Planning

```python
from geo_infer_bio import ConservationPlanner

# Plan conservation areas
planner = ConservationPlanner()

plan = planner.prioritize(
    targets=species_targets,
    cost_layer=land_costs,
    budget=10_000_000)

print(f"Priority areas: {plan.selected_areas}")```

### 4. Biodiversity Metrics

```python
from geo_infer_bio import BiodiversityCalculator

# Calculate biodiversity metrics
calc = BiodiversityCalculator()

metrics = calc.compute(
    species_data=survey_data,
    indices=["shannon", "simpson", "species_richness"])

print(f"Shannon index: {metrics.shannon}")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **SDM** | ✅ Ready | MaxEnt, RF models |
| **Habitat** | ✅ Ready | Connectivity, quality |
| **Conservation** | ✅ Ready | Marxan, prioritization |
| **Metrics** | ✅ Ready | Diversity indices |

### Aspirational Features

- 🔮 **BiodiversityAgent**: Monitoring automation
- 🔮 **ConservationAgent**: Adaptive management

---

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
