---
title: "GEO-INFER-METAGOV: Meta-Governance Framework"
description: "Governance frameworks, policy management, and institutional modeling"
purpose: "Enable governance modeling and multi-stakeholder coordination"
module_type: "Governance"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["NORMS", "CIV"]
compatibility: ["GEO-INFER-NORMS", "GEO-INFER-CIV", "GEO-INFER-ORG"]
tags: ["governance", "policy", "institutions", "coordination", "rules"]
difficulty: "Advanced"
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

# GEO-INFER-METAGOV: Meta-Governance Framework

## Overview

**GEO-INFER-METAGOV** provides spatial governance modeling, multi-scale jurisdictional analysis, and cross-boundary coordination tools. It addresses the problem of overlapping governance structures -- where municipal, county, state, regional, tribal, and federal authorities share spatial jurisdiction -- by analyzing overlap, identifying gaps, and modeling multi-stakeholder coordination processes. The module supports polycentric governance patterns grounded in Elinor Ostrom's institutional analysis framework.

## Core Objectives

- **Jurisdictional Overlap Detection**: Identify and quantify regions where multiple governance authorities share spatial jurisdiction, flagging conflicts and coordination gaps
- **Governance Quality Assessment**: Compute composite governance indices from participation, transparency, accountability, and effectiveness indicators
- **Multi-Scale Coordination Modeling**: Model how decisions propagate across nested governance hierarchies (municipal to federal) with feedback loops
- **Adaptive Policy Simulation**: Simulate policy adjustment scenarios and evaluate governance outcomes over time using Active Inference principles

## Features

### Policy Management

```python
from geo_infer_metagov import PolicyManager

# Manage spatial policies
manager = PolicyManager()

manager.add_policy(
    name="conservation_zone",
    rules=["no_development", "restricted_access"],
    area=protected_area
)
```

### Institutional Modeling

```python
from geo_infer_metagov import InstitutionModel

# Model governance institution
model = InstitutionModel()

model.define(
    name="watershed_council",
    stakeholders=["agencies", "communities", "ngo"],
    decision_rules="consensus"
)
```

### Multi-Stakeholder Coordination

```python
from geo_infer_metagov import StakeholderCoordinator

# Coordinate stakeholders
coordinator = StakeholderCoordinator()

agreement = coordinator.negotiate(
    parties=stakeholders,
    issue="resource_allocation",
    method="mediation"
)
```

### Adaptive Governance

```python
from geo_infer_metagov import AdaptiveGovernance

# Adapt rules based on outcomes
adaptive = AdaptiveGovernance()

adaptive.adjust(
    policy=current_policy,
    feedback=monitoring_data
)
```

## API Reference

| Class / Function | Description |
|------------------|-------------|
| `MetagovAnalyzer(config)` | Primary analyzer for governance structures with configurable scale and metrics |
| `GovernanceMapper(jurisdiction_layers)` | Maps governance boundaries and authority hierarchies across spatial scales |
| `JurisdictionOverlapAnalyzer()` | Detects overlapping jurisdictions from multiple GeoDataFrame boundary layers |
| `JurisdictionOverlapAnalyzer.find_overlaps(layers)` | Returns GeoDataFrame of overlap polygons with authority metadata |
| `MetagovAnalyzer.compute_governance_index(data)` | Computes weighted composite governance quality index from indicator dict |
| `PolicyManager.add_policy(name, rules, area)` | Registers a spatial policy with enforcement rules over a geometry |
| `StakeholderCoordinator.negotiate(parties, issue, method)` | Runs negotiation simulation among stakeholder parties |
| `AdaptiveGovernance.adjust(policy, feedback)` | Adjusts policy parameters based on monitoring feedback |

## Governance Models

| Model | Description |
|-------|-------------|
| **Command** | Top-down |
| **Network** | Collaborative |
| **Polycentric** | Multi-center |
| **Adaptive** | Learning-based |

## Working Code Examples

### Example 1: Jurisdiction Overlap Analysis

```python
from geo_infer_metagov.core.jurisdiction_analyzer import JurisdictionOverlapAnalyzer
import geopandas as gpd

# Load jurisdiction boundaries (municipal, county, regional)
municipal = gpd.read_file("municipal_boundaries.geojson")
county = gpd.read_file("county_boundaries.geojson")

analyzer = JurisdictionOverlapAnalyzer()
overlaps = analyzer.find_overlaps([municipal, county])
print(f"Found {len(overlaps)} jurisdictional overlaps")
```

### Example 2: Governance Quality Index

```python
from geo_infer_metagov.core.metagov_analyzer import MetagovAnalyzer

analyzer = MetagovAnalyzer(config={"scale": "regional"})
governance_data = {
    "participation_rate": 0.35,
    "transparency_score": 0.72,
    "accountability_index": 0.68,
}
quality_index = analyzer.compute_governance_index(governance_data)
print(f"Governance quality index: {quality_index:.3f}")
```

## Integration

GEO-INFER-METAGOV integrates with the following modules:

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-CIV** | METAGOV <-- CIV | Civic participation data and community boundaries |
| **GEO-INFER-NORMS** | METAGOV <-> NORMS | Normative rules feed governance models; governance outcomes update norms |
| **GEO-INFER-DATA** | METAGOV <-- DATA | Census, administrative, and survey datasets |
| **GEO-INFER-SPACE** | METAGOV <-- SPACE | Spatial operations for jurisdiction geometry analysis |
| **GEO-INFER-ORG** | METAGOV --> ORG | Governance structures inform organizational modeling |

Data flow: CIV, DATA, and SPACE provide boundary geometries, civic indicators, and spatial operations. METAGOV computes governance indices and jurisdictional analysis. Results feed into NORMS for rule updates and ORG for organizational design.

## Installation

```bash
uv pip install -e "./GEO-INFER-METAGOV"
```

## Testing

```bash
# Run all METAGOV tests
uv run python -m pytest GEO-INFER-METAGOV/tests/ -v

# Run unit tests only
uv run python -m pytest GEO-INFER-METAGOV/tests/unit/ -v

# Run with coverage
uv run python -m pytest GEO-INFER-METAGOV/tests/ --cov=GEO-INFER-METAGOV/src --cov-report=html
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
