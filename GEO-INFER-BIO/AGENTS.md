# GEO-INFER-BIO: Biodiversity Intelligence Agents

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


The GEO-INFER-BIO module provides biodiversity and ecological analysis capabilities enabling intelligent agents to monitor species distributions, analyze ecosystem health, and support conservation planning.

## Implementation Status

### Currently Implemented

- ✅ **SpeciesDistributionModeler**: SDM and habitat suitability
- ✅ **BiodiversityAnalyzer**: Diversity metrics and patterns
- ✅ **EcosystemHealthAssessor**: Ecosystem condition assessment
- ✅ **ConservationPlanner**: Protected area optimization

### Aspirational/Planned Features

- 🔮 **WildlifeMonitoringAgent**: Autonomous species tracking
- 🔮 **ConservationAgent**: Adaptive conservation management

## Agent Capabilities Supported

### 1. Species Distribution Modeling

```python
from geo_infer_bio import SpeciesDistributionModeler

# Agent models species habitat
modeler = SpeciesDistributionModeler()
habitat_map = modeler.model(
    occurrences=species_records,
    environmental_layers=climate_data,
    method='maxent'
)
```

### 2. Biodiversity Analysis

```python
from geo_infer_bio import BiodiversityAnalyzer

# Biodiversity assessment
analyzer = BiodiversityAnalyzer()
diversity = analyzer.analyze(
    community_data=species_observations,
    metrics=['richness', 'shannon', 'simpson']
)
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Species Distribution** | ✅ Ready | Habitat modeling |
| **Biodiversity Analysis** | ✅ Ready | Diversity metrics |
| **Ecosystem Health** | ✅ Ready | Condition assessment |
| **Conservation Planning** | ✅ Ready | Protected area optimization |
| **Wildlife Monitoring** | 🔮 Planned | Autonomous tracking |

---

This AGENTS.md documents how GEO-INFER-BIO provides biodiversity intelligence capabilities for the agent ecosystem.
