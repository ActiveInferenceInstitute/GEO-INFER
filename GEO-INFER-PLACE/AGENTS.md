
<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---
# GEO-INFER-PLACE: Place-Based Analysis Framework Support

## Overview

The GEO-INFER-PLACE module provides place-based analysis capabilities enabling agents to understand the unique characteristics, identity, and significance of geographic places.

## Implementation Status

### Currently Implemented

- ✅ **PlaceCharacterizer**: Place identity and attributes
- ✅ **SenseOfPlaceAnalyzer**: Qualitative place assessment
- ✅ **PlaceNameResolver**: Geocoding and toponymy
- ✅ **ContextualAnalyzer**: Local context assessment

### Aspirational/Planned Features

- 🔮 **PlaceExplorationAgent**: Autonomous place discovery
- 🔮 **LocalKnowledgeAgent**: Community knowledge integration

## Agent Capabilities Supported

### 1. Place Characterization

```python
from geo_infer_place import PlaceCharacterizer

# Agent characterizes place
characterizer = PlaceCharacterizer()
place_profile = characterizer.characterize(
    location=target_location,
    aspects=['physical', 'social', 'cultural', 'economic']
)
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Place Characterization** | ✅ Ready | Identity analysis |
| **Sense of Place** | ✅ Ready | Qualitative assessment |
| **Name Resolution** | ✅ Ready | Geocoding |
| **Contextual Analysis** | ✅ Ready | Local context |
| **Exploration Agent** | 🔮 Planned | Autonomous discovery |

---

This AGENTS.md documents how GEO-INFER-PLACE provides place-based analysis capabilities.
