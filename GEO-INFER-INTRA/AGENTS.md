# GEO-INFER-INTRA: Internal Documentation Framework

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


The GEO-INFER-INTRA module provides documentation and knowledge management capabilities serving as the central documentation hub for the GEO-INFER framework.

## Implementation Status

### Currently Implemented

- ✅ **DocumentationGenerator**: Automated documentation
- ✅ **KnowledgeBase**: Centralized knowledge repository
- ✅ **ModuleRegistry**: Module catalog and discovery
- ✅ **CrossReferencer**: Inter-module linking

### Aspirational/Planned Features

- 🔮 **DocumentationAgent**: Automated documentation updates
- 🔮 **KnowledgeExtractionAgent**: Knowledge discovery

## Agent Capabilities Supported

### 1. Knowledge Access

```python
from geo_infer_intra import KnowledgeBase

# Agent accesses documentation
kb = KnowledgeBase()
docs = kb.query(
    topic="active_inference",
    modules=['ACT', 'AGENT']
)
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Documentation** | ✅ Ready | Auto-generated docs |
| **Knowledge Base** | ✅ Ready | Centralized knowledge |
| **Module Registry** | ✅ Ready | Module catalog |
| **Cross-Reference** | ✅ Ready | Inter-module links |
| **Doc Agent** | 🔮 Planned | Auto-updates |

---

This AGENTS.md documents how GEO-INFER-INTRA provides documentation capabilities.
