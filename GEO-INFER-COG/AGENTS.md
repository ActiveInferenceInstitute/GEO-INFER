# GEO-INFER-COG: Cognitive Modeling Framework

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---


## Overview

The GEO-INFER-COG module provides cognitive modeling capabilities enabling intelligent agents to incorporate human-like cognitive processes including attention, memory, and decision-making heuristics.

## Implementation Status

### Currently Implemented

- ✅ **AttentionModel**: Selective attention mechanisms
- ✅ **MemorySystem**: Working and long-term memory
- ✅ **DecisionHeuristics**: Cognitive decision patterns
- ✅ **MentalModelRepresentation**: Internal world models

### Aspirational/Planned Features

- 🔮 **CognitiveAgent**: Full cognitive architecture integration
- 🔮 **TheoryOfMindAgent**: Multi-agent mental modeling

## Agent Capabilities Supported

### 1. Attention Mechanisms

```python
from geo_infer_cog import AttentionModel

# Agent attention allocation
attention = AttentionModel()
focused = attention.allocate(
    information=incoming_data,
    priorities=task_relevance,
    capacity=cognitive_load_limit
)
```

### 2. Memory Systems

```python
from geo_infer_cog import MemorySystem

# Agent memory operations
memory = MemorySystem()
memory.store(experience=recent_observation, context=spatial_context)
recalled = memory.retrieve(query=current_situation)
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Attention** | ✅ Ready | Selective focus |
| **Memory** | ✅ Ready | Information storage |
| **Heuristics** | ✅ Ready | Decision patterns |
| **Mental Models** | ✅ Ready | World representation |
| **Cognitive Agent** | 🔮 Planned | Full architecture |

---

This AGENTS.md documents how GEO-INFER-COG provides cognitive modeling capabilities for the agent ecosystem.
