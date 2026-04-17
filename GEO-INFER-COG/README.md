---
title: "GEO-INFER-COG: Cognitive Spatial Reasoning"
description: "Spatial cognition modeling, cognitive maps, and human-centered geospatial processing"
purpose: "Cognitive-science-grounded spatial reasoning for agents and user interfaces"
module_type: "Core Intelligence"
status: "Alpha"
last_updated: "2026-04-16"
dependencies: ["SPACE", "ACT", "AI"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-ACT", "GEO-INFER-APP", "GEO-INFER-EDU", "GEO-INFER-AI"]
tags: ["cognition", "spatial-reasoning", "mental-maps", "wayfinding", "decision-support"]
difficulty: "Advanced"
estimated_time: "40"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> •
  <a href="../README.md#-module-overview">Module Index</a> •
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-COG: Cognitive Spatial Reasoning

## Overview

**GEO-INFER-COG** implements cognitive-science-grounded models of spatial perception, reasoning, memory, and language for geospatial workflows. The module is organized around a `CognitiveProcessingEngine` that coordinates perception, reasoning, memory, and decision components, plus data models for cognitive maps and user profiles. It supports human-centered visualization and spatial decision support for both interactive applications and autonomous agents.

## Core Components

- **CognitiveProcessingEngine** — orchestrates perception → reasoning → memory → decision
- **SpatialPerceptionModel** — landmark salience, region recognition, distance estimation
- **SpatialReasoningEngine** — route reasoning, topological inference, frame-of-reference transforms
- **SpatialMemoryModel** — cognitive map construction, rehearsal, decay, landmark consolidation
- **SpatialLanguageProcessor** — parses and generates spatial natural language (e.g. "north of the park")
- **HumanCenteredVisualizer** — cognitively-informed map styling and saliency-aware rendering
- **SpatialDecisionSupport** — multi-criteria decision under cognitive load constraints
- **CognitiveMap, SpatialKnowledgeGraph, UserCognitiveProfile** — typed models for cognitive state

## Features

### Cognitive Processing Pipeline

```python
from geo_infer_cog import CognitiveProcessingEngine, UserCognitiveProfile

profile = UserCognitiveProfile(working_memory_capacity=7, strategy="landmark_based")
engine = CognitiveProcessingEngine(profile=profile)

result = engine.process(
    observation={"landmarks": [...], "route": [...]},
    task="wayfinding",
)
print(result.decision, result.confidence)
```

### Cognitive Map Construction

```python
from geo_infer_cog import SpatialMemoryModel, CognitiveMap

memory = SpatialMemoryModel(decay_rate=0.05)
cmap: CognitiveMap = memory.build_map(
    observations=gps_traces,
    landmarks=poi_list,
)
print(f"Landmarks retained: {len(cmap.landmarks)}")
```

### Spatial Language

```python
from geo_infer_cog import SpatialLanguageProcessor

slp = SpatialLanguageProcessor()
parsed = slp.parse("the cafe just north of the library")
# -> {relation: 'north_of', figure: 'cafe', ground: 'library', proximity: 'near'}
```

### Human-Centered Visualization

```python
from geo_infer_cog import HumanCenteredVisualizer

viz = HumanCenteredVisualizer()
styled = viz.style_map(
    base_map=folium_map,
    user_profile=profile,
    emphasize=["landmarks", "route"],
)
```

### Decision Support

```python
from geo_infer_cog import SpatialDecisionSupport

dss = SpatialDecisionSupport()
ranked = dss.rank_options(
    alternatives=route_candidates,
    criteria={"distance": -1.0, "landmarks": 2.0, "complexity": -1.5},
    user_profile=profile,
)
```

## API Reference

| Class | Purpose |
|-------|---------|
| `CognitiveProcessingEngine(profile, ...)` | Coordinates perception/reasoning/memory/decision |
| `SpatialPerceptionModel(...)` | Landmark salience, region recognition |
| `SpatialReasoningEngine(...)` | Topology, frame transforms, route reasoning |
| `SpatialMemoryModel(decay_rate, ...)` | Cognitive-map construction with decay |
| `SpatialLanguageProcessor()` | Spatial NL parsing and generation |
| `HumanCenteredVisualizer()` | Cognitively-informed styling for folium/plotly |
| `SpatialDecisionSupport()` | Weighted multi-criteria decision with cognitive-load ceiling |
| `CognitiveMap`, `SpatialKnowledgeGraph` | Data models for cognitive state |
| `UserCognitiveProfile(working_memory_capacity, strategy, ...)` | Per-user cognitive parameters |

## Utility Functions

| Function | Purpose |
|----------|---------|
| `validate_spatial_data(data)` | Shape/CRS/schema checks for spatial inputs |
| `validate_cognitive_model(model)` | Structural validation of cognitive models |
| `load_cognitive_profile(path)` | Load persisted `UserCognitiveProfile` |
| `save_cognitive_model(model, path)` | Persist cognitive state to disk |
| `create_cog_api_app()` | FastAPI app exposing COG endpoints (optional) |

## Cognitive Models

| Model | Application |
|-------|-------------|
| Landmark salience | Route descriptions, map simplification |
| Mental rotation | 3D visualization, multi-view reasoning |
| Perspective taking | Shared-map interaction, collaborative planning |
| Cognitive-load ceiling | UI information density, decision-support throttling |

## Integration

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-SPACE** | COG ← SPACE | H3 operations and geometry for spatial models |
| **GEO-INFER-ACT** | COG ↔ ACT | Feeds perception/memory into active-inference agents |
| **GEO-INFER-AI** | COG ↔ AI | Learned saliency/attention models as COG priors |
| **GEO-INFER-APP** | COG → APP | Cognitively-informed UI recommendations |
| **GEO-INFER-EDU** | COG → EDU | Learner models for adaptive content |

## Installation

```bash
uv pip install -e "./GEO-INFER-COG"
```

## Testing

```bash
uv run python -m pytest GEO-INFER-COG/tests/ -v
uv run python -m pytest GEO-INFER-COG/tests/ --cov=GEO-INFER-COG/src --cov-report=html
```

## Documentation Hub

Full framework documentation is in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation and quick-start |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | Cross-module workflows |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards |

---

**Status**: Alpha — research implementation

**Last Updated**: 2026-04-16
