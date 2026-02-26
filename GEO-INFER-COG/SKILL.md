---
name: geo-infer-cog
description: Cognitive modeling for geospatial agents including attention, memory, and trust. Use when implementing spatial attention mechanisms, working memory for geographic contexts, or trust dynamics in multi-agent geospatial systems.
prerequisites:
  required:
    - geo-infer-act
  recommended:
    - geo-infer-bayes
    - geo-infer-space
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-COG

## Instructions

### Core Capabilities

- **Spatial attention**: Selective attention to geographic regions
- **Working memory**: Context-dependent spatial memory buffers
- **Trust dynamics**: Agent trust modeling in collaborative environments
- **Cognitive load**: Resource allocation for spatial reasoning
- **Mental models**: Internal representations of spatial environments

### Key Imports

```python
from geo_infer_cog.core.attention import SpatialAttention
from geo_infer_cog.core.memory import WorkingMemory
from geo_infer_cog.core.trust import TrustModel
```

## Examples

```python
from geo_infer_cog.core.attention import SpatialAttention

attention = SpatialAttention(resolution=7)
salience_map = attention.compute(observations, priors)
focus_region = attention.select_focus(salience_map)
```

## Guidelines

- Currently Alpha status — attention and memory models in development

### Integrations

- Integrates with ACT for Active Inference-based cognitive architectures
- Test: `uv run python -m pytest GEO-INFER-COG/tests/ -v`
