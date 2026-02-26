---
title: "GEO-INFER-COG: Cognitive Spatial Reasoning"
description: "Spatial cognition modeling, mental maps, and human-agent interaction"
purpose: "Provide cognitive science-based spatial reasoning for agents"
module_type: "Core Intelligence"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "ACT"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-ACT", "GEO-INFER-EDU"]
tags: ["cognition", "spatial-reasoning", "mental-maps", "wayfinding"]
difficulty: "Advanced"
estimated_time: "40"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-COG: Cognitive Spatial Reasoning

## Overview

**GEO-INFER-COG** provides cognitive science-based capabilities for spatial reasoning:

- **Spatial Cognition**: Human-like spatial thinking models
- **Mental Maps**: Cognitive map analysis and generation
- **Wayfinding**: Navigation strategy modeling
- **Attention Models**: Visual attention in spatial contexts

## Features

### Spatial Cognition Modeling

```python
from geo_infer_cog import SpatialCognitionModel

# Model human spatial reasoning
model = SpatialCognitionModel()

# Analyze wayfinding behavior
behavior = model.analyze_wayfinding(
    route_data=gps_traces,
    environment=building_layout
)

print(f"Decision points: {behavior.decision_points}")
print(f"Cognitive load: {behavior.cognitive_load}")
```

### Mental Map Analysis

```python
from geo_infer_cog import MentalMapAnalyzer

# Analyze cognitive maps
analyzer = MentalMapAnalyzer()

analysis = analyzer.compare(
    sketch_maps=participant_sketches,
    ground_truth=actual_map
)

print(f"Distortion: {analysis.distortion_score}")
print(f"Key landmarks: {analysis.landmarks}")
```

### Attention Modeling

```python
from geo_infer_cog import AttentionModel

# Model visual attention
attention = AttentionModel()

saliency = attention.compute(
    scene=urban_image,
    task="navigation"
)

print(f"Attention hotspots: {saliency.hotspots}")
```

### Cognitive Agent

```python
from geo_infer_cog import CognitiveAgent

# Create cognitively-inspired agent
agent = CognitiveAgent(
    working_memory_capacity=7,
    attention_model="top_down"
)

route = agent.plan_route(
    origin=start,
    destination=end,
    strategy="landmark_based"
)
```

## Cognitive Models

| Model | Application |
|-------|-------------|
| **Spatial Reasoning** | Navigation, planning |
| **Mental Rotation** | 3D visualization |
| **Perspective Taking** | Multi-viewpoint |
| **Cognitive Load** | UI optimization |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-EDU** | Learning adaptation |
| **GEO-INFER-APP** | UX design |
| **GEO-INFER-SPACE** | Spatial operations |

## Installation

```bash
uv pip install -e "./GEO-INFER-COG"
```

## Related Documentation

- [GEO-INFER-EDU](../GEO-INFER-EDU/README.md): Education
- [AGENTS.md](./AGENTS.md): Cognitive capabilities

---

**Status**: Alpha - Research implementation

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
