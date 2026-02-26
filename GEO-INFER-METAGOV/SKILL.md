---
name: geo-infer-metagov
description: Meta-governance frameworks for geospatial decision-making. Use when implementing polycentric governance, multi-level institutional analysis, stakeholder engagement, conflict resolution, or adaptive governance scenarios for spatial resource management.
prerequisites:
  required:
    - geo-infer-data
    - geo-infer-api
  recommended:
    - geo-infer-norms
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-METAGOV

## Instructions

### Core Capabilities

- **Polycentric governance**: Multi-center decision structures (Ostrom framework)
- **Multi-level analysis**: Institutional analysis across governance scales
- **Stakeholder management**: Stakeholder mapping, power analysis, engagement tracking
- **Conflict resolution**: Spatial conflict detection, mediation workflows
- **Adaptation**: Adaptive governance, scenario planning, performance monitoring
- **Accountability**: Decision tracking, audit trails, transparency metrics

### Key Imports

```python
from geo_infer_metagov.core.polycentric import PolycentricGovernance
from geo_infer_metagov.core.stakeholder import StakeholderAnalyzer
from geo_infer_metagov.core.conflict_resolution import ConflictResolver
from geo_infer_metagov.core.adaptation import AdaptiveGovernance
from geo_infer_metagov.core.accountability import AccountabilityTracker
```

## Examples

```python
from geo_infer_metagov.core.stakeholder import StakeholderAnalyzer

analyzer = StakeholderAnalyzer()
analyzer.register("community_group", power=0.3, interest=0.9)
analyzer.register("government", power=0.8, interest=0.6)
matrix = analyzer.build_power_interest_matrix()
priority_engagement = analyzer.recommend_strategies()
```

## Guidelines

- DAO mechanisms in development (Alpha)

### Integrations

- Integrates with NORMS for normative governance checks
- Integrates with CIV for participatory governance
- Test: `uv run python -m pytest GEO-INFER-METAGOV/tests/ -v`
