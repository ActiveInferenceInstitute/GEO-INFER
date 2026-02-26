---
title: "GEO-INFER-PEP: People Engagement Platform"
description: "Community engagement, constituent mapping, and outreach optimization"
purpose: "Enable place-based community engagement and constituent relationship management"
module_type: "Community & Applications"
status: "Stable"
last_updated: "2026-02-25"
dependencies: ["SPACE", "CIV", "COMMS"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-CIV", "GEO-INFER-COMMS", "GEO-INFER-DATA"]
tags: ["engagement", "crm", "outreach", "community", "constituent"]
difficulty: "Intermediate"
estimated_time: "30"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> |
  <a href="../README.md#-module-overview">Module Index</a> |
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-PEP: People Engagement Platform

## Overview

**GEO-INFER-PEP** provides a spatial constituent relationship management (CRM) platform for place-based communities. It maps constituent engagement across geographic space, optimizes outreach campaigns under budget constraints, and tracks the effectiveness of community engagement programs. The module is designed for civic organizations, municipal governments, and nonprofits that need to understand and improve how they reach their constituents across a spatial service area.

## Core Objectives

- **Spatial Engagement Mapping**: Aggregate constituent engagement scores onto H3 hexagonal grids to visualize engagement hotspots and cold zones across a service area
- **Budget-Constrained Outreach Optimization**: Maximize constituent reach across multiple channels (email, SMS, door-to-door) within a fixed budget using optimization algorithms
- **Constituent Lifecycle Tracking**: Track constituent interactions over time with spatial context, identifying churn risk and re-engagement opportunities
- **Multi-Channel Campaign Analytics**: Measure campaign effectiveness by channel, geography, and demographic segment

## Features

### Proposal Submission

```python
from geo_infer_pep import ProposalManager

# Submit enhancement proposal
manager = ProposalManager()

proposal = manager.submit(
    title="Add H3 v5 Support",
    type="feature",
    description="Upgrade to H3 version 5",
    affected_modules=["SPACE", "DATA"]
)

print(f"PEP ID: {proposal.pep_id}")
```

### Review Coordination

```python
from geo_infer_pep import ReviewCoordinator

# Coordinate reviews
coordinator = ReviewCoordinator()

review = coordinator.initiate(
    proposal=pep_id,
    reviewers=["maintainer_1", "expert_1"]
)

print(f"Status: {review.status}")
```

### Decision Tracking

```python
from geo_infer_pep import DecisionTracker

# Record decisions
tracker = DecisionTracker()

tracker.record(
    pep_id="PEP-2026-003",
    decision="accepted",
    rationale="Community support"
)
```

## API Reference

| Class / Function | Description |
|------------------|-------------|
| `EngagementAnalyzer(config)` | Analyzes constituent engagement patterns across spatial and temporal dimensions |
| `ConstituentMapper(h3_resolution)` | Maps constituent records to H3 cells and computes spatial engagement aggregates |
| `OutreachOptimizer(budget_constraint)` | Optimizes multi-channel outreach campaigns within a budget constraint |
| `ConstituentMapper.aggregate_to_h3(gdf)` | Aggregates a GeoDataFrame of constituents to H3-level engagement scores |
| `OutreachOptimizer.optimize_coverage(target_population, channels, cost_per_contact)` | Returns an optimized outreach plan with channel allocation and estimated reach |
| `EngagementAnalyzer.compute_churn_risk(constituents, window_days)` | Identifies constituents at risk of disengagement based on contact recency |
| `EngagementAnalyzer.segment_by_engagement(constituents, n_segments)` | Clusters constituents into engagement tiers (high, medium, low, inactive) |

## PEP Types

| Type | Description |
|------|-------------|
| **Feature** | New functionality |
| **Architecture** | Structural changes |
| **Process** | Process improvements |
| **Deprecation** | Feature removal |

## PEP Status

| Status | Meaning |
|--------|---------|
| **Draft** | Under development |
| **Review** | Under review |
| **Accepted** | Approved |
| **Implemented** | Complete |
| **Rejected** | Not approved |

## Working Code Examples

### Example 1: Constituent Engagement Mapping

```python
from geo_infer_pep.core.constituent_mapper import ConstituentMapper
import geopandas as gpd
from shapely.geometry import Point

# Map constituent locations with engagement scores
constituents = gpd.GeoDataFrame(
    {
        "id": range(50),
        "engagement_score": [float(i % 5) / 4 for i in range(50)],
        "last_contact": ["2024-01-01"] * 50,
        "geometry": [Point(-122.33 + i * 0.002, 47.61 + i * 0.002) for i in range(50)],
    },
    crs="EPSG:4326",
)

mapper = ConstituentMapper(h3_resolution=9)
engagement_map = mapper.aggregate_to_h3(constituents)
print(f"High-engagement cells: {(engagement_map['score'] > 0.7).sum()}")
```

### Example 2: Outreach Optimization

```python
from geo_infer_pep.core.outreach_optimizer import OutreachOptimizer

optimizer = OutreachOptimizer(budget_constraint=1000.0)
outreach_plan = optimizer.optimize_coverage(
    target_population=constituents,
    channels=["email", "sms", "door_to_door"],
    cost_per_contact={"email": 0.5, "sms": 1.0, "door_to_door": 15.0},
)
print(f"Estimated reach: {outreach_plan['estimated_reach']} constituents")
```

## Integration

GEO-INFER-PEP integrates with the following modules:

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-SPACE** | PEP <-- SPACE | H3 spatial aggregation for engagement mapping |
| **GEO-INFER-CIV** | PEP <-- CIV | Civic participation data and community boundaries |
| **GEO-INFER-COMMS** | PEP --> COMMS | Outreach plans trigger notifications and messaging |
| **GEO-INFER-DATA** | PEP <-- DATA | Constituent records and demographic datasets |
| **GEO-INFER-ECON** | PEP <-- ECON | Economic indicators for outreach prioritization |

Data flow: DATA and CIV provide constituent records and civic context. SPACE provides H3 spatial operations. PEP analyzes engagement patterns, optimizes outreach plans, and hands off campaign execution to COMMS.

## Installation

```bash
uv pip install -e "./GEO-INFER-PEP"
```

## Testing

```bash
# Run all PEP tests
uv run python -m pytest GEO-INFER-PEP/tests/ -v

# Run unit tests only
uv run python -m pytest GEO-INFER-PEP/tests/unit/ -v

# Run with coverage
uv run python -m pytest GEO-INFER-PEP/tests/ --cov=GEO-INFER-PEP/src --cov-report=html
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

**Status**: Stable

**Last Updated**: 2026-02-25
