---
title: "GEO-INFER-CIV: Civic Engagement and Participation"
description: "Civic engagement, participatory planning, and democratic decision-making"
purpose: "Enable community participation and collaborative governance in geospatial contexts"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-01-26"
dependencies: ["SPACE", "APP", "COMMS"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-APP", "GEO-INFER-COMMS"]
tags: ["civic", "participation", "democracy", "community", "engagement"]
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

# GEO-INFER-CIV: Civic Engagement and Participation

## Overview

**GEO-INFER-CIV** provides civic engagement capabilities:

- **Community Participation**: Collect and analyze community input
- **Participatory Mapping**: Community-driven map contributions
- **Consensus Building**: Multi-stakeholder decision support
- **Transparency**: Public accountability reporting

## Features

### Participation Platform

```python
from geo_infer_civ import ParticipationPlatform

# Collect community input
platform = ParticipationPlatform()

feedback = platform.collect(
    topic="downtown_redesign",
    methods=["survey", "map_comments", "forum"],
    duration_days=30
)

print(f"Responses: {feedback.count}")
print(f"Key themes: {feedback.themes}")
```

### Participatory Mapping

```python
from geo_infer_civ import ParticipatoryMapper

# Enable community mapping
mapper = ParticipatoryMapper()

session = mapper.create_session(
    topic="neighborhood_improvements",
    contribution_types=["point", "comment", "polygon"]
)

# Aggregate contributions
aggregated = mapper.aggregate(session)
print(f"Hotspots: {aggregated.hotspots}")
```

### Consensus Building

```python
from geo_infer_civ import ConsensusBuilder

# Build consensus among stakeholders
builder = ConsensusBuilder()

result = builder.facilitate(
    stakeholders=community_groups,
    alternatives=planning_options,
    method="multi_criteria"
)

print(f"Consensus level: {result.consensus}%")
print(f"Preferred option: {result.choice}")
```

### Transparency Reporting

```python
from geo_infer_civ import TransparencyReporter

# Generate transparency report
reporter = TransparencyReporter()

report = reporter.generate(
    project="park_renovation",
    period=("2025-01", "2025-12")
)

print(f"Budget used: {report.budget_percent}%")
print(f"Community input addressed: {report.input_addressed}")
```

## Engagement Methods

| Method | Use Case |
|--------|----------|
| **Surveys** | Structured feedback |
| **Map Comments** | Location-specific input |
| **Forums** | Open discussion |
| **Voting** | Decision making |
| **Workshops** | In-depth engagement |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-APP** | Web interfaces |
| **GEO-INFER-COMMS** | Notifications |
| **GEO-INFER-METAGOV** | Governance |

## Installation

```bash
uv pip install -e "./GEO-INFER-CIV"
```

## Related Documentation

- [GEO-INFER-METAGOV](../GEO-INFER-METAGOV/README.md): Governance
- [AGENTS.md](./AGENTS.md): Civic capabilities

---

**Status**: Alpha

**Last Updated**: 2026-01-26
