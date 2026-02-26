---
title: "GEO-INFER-HEALTH: Public Health and Epidemiology"
description: "Disease mapping, health disparities, and epidemiological analysis"
purpose: "Enable spatial health analysis and public health decision support"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "TIME", "DATA"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-SPM"]
tags: ["health", "epidemiology", "disease-mapping", "public-health"]
difficulty: "Intermediate"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-HEALTH: Public Health and Epidemiology

## Overview

**GEO-INFER-HEALTH** provides spatial health analysis:

- **Disease Mapping**: Incidence and prevalence mapping
- **Cluster Detection**: Outbreak identification
- **Health Disparities**: Access and equity analysis
- **Exposure Assessment**: Environmental health

## Features

### Disease Mapping

```python
from geo_infer_health import DiseaseMapper

# Map disease patterns
mapper = DiseaseMapper()

map = mapper.create(
    cases=disease_cases,
    population=population_data,
    smoothing="bayesian"
)

print(f"High risk areas: {map.hotspots}")
```

### Cluster Detection

```python
from geo_infer_health import ClusterDetector

# Detect disease clusters
detector = ClusterDetector()

clusters = detector.detect(
    cases=outbreak_data,
    method="kulldorff_scan",
    max_radius_km=50
)

print(f"Clusters found: {len(clusters)}")
```

### Health Access Analysis

```python
from geo_infer_health import HealthAccessAnalyzer

# Analyze healthcare access
access = HealthAccessAnalyzer()

analysis = access.analyze(
    facilities=healthcare_facilities,
    population=census_data,
    mode="driving"
)

print(f"Underserved areas: {analysis.gaps}")
```

### Environmental Health

```python
from geo_infer_health import EnvironmentalHealth

# Assess health exposures
env = EnvironmentalHealth()

exposure = env.assess(
    population=residents,
    hazards=pollution_sources,
    pathways=["air", "water"]
)
```

## Analysis Types

| Type | Application |
|------|-------------|
| **SMR** | Standardized rates |
| **Bayesian** | Small area estimation |
| **Scan** | Cluster detection |
| **Accessibility** | Service coverage |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-SPM** | Spatial statistics |
| **GEO-INFER-TIME** | Temporal patterns |

## Installation

```bash
uv pip install -e "./GEO-INFER-HEALTH"
```

---

**Status**: Alpha

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
