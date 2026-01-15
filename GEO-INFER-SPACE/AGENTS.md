# GEO-INFER-SPACE: Spatial Intelligence Framework

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


The GEO-INFER-SPACE module provides foundational spatial capabilities that power the intelligent agent ecosystem. It enables agents to perceive, reason about, and act within geospatial environments using H3 v4 indexing, spatial analysis, and coordinate transformations.

## Implementation Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational.

### Currently Implemented

- ✅ **H3Manager**: Hierarchical spatial indexing with H3 v4
- ✅ **NestedH3Systems**: Hierarchical grid management (Verified)
- ✅ **Zero Mock Policy**: Full compliance in `src` and tests
- ✅ **SpatialAnalyzer**: Comprehensive spatial analysis toolkit
- ✅ **CoordinateTransformer**: Multi-CRS coordinate transformations
- ✅ **TopologyEngine**: Spatial relationship analysis
- ✅ **ProximityCalculator**: Distance and buffer operations

### Aspirational/Planned Features

- 🔮 **SpatialBeliefPropagation**: Belief propagation over spatial networks
- 🔮 **SpatialGenerativeModel**: Generative models for spatial prediction

## Agent Capabilities Supported

### 1. Spatial Perception

SPACE enables agents to perceive and interpret their spatial environment:

```python
from geo_infer_space import H3Manager, SpatialAnalyzer

# Initialize spatial perception
h3_manager = H3Manager()
analyzer = SpatialAnalyzer()

# Agent perceives spatial context
current_cell = h3_manager.geo_to_h3(
    lat=agent_position[0],
    lng=agent_position[1],
    resolution=9
)

# Get surrounding context
neighbors = h3_manager.get_k_ring(current_cell, k=2)
local_features = analyzer.extract_features(neighbors)
```

### 2. Spatial Reasoning

SPACE supports spatial reasoning for agent decision-making:

```python
from geo_infer_space import TopologyEngine, ProximityCalculator

# Spatial relationship analysis
topology = TopologyEngine()
proximity = ProximityCalculator()

# Agent reasons about spatial relationships
nearby_resources = proximity.within_distance(
    agent_position,
    resource_locations,
    max_distance=1000  # meters
)

# Analyze spatial topology
connectivity = topology.analyze_connectivity(
    origin=current_location,
    destinations=target_locations,
    network=transportation_graph
)
```

### 3. Spatial Action

SPACE enables agents to plan and execute spatially-aware actions:

```python
from geo_infer_space import PathPlanner, SpatialOptimizer

# Path planning for agent navigation
planner = PathPlanner()
optimizer = SpatialOptimizer()

# Agent plans route
optimal_path = planner.find_path(
    origin=current_position,
    destination=target_position,
    constraints={'avoid_obstacles': True, 'minimize_distance': True}
)

# Optimize spatial coverage
coverage_plan = optimizer.optimize_coverage(
    target_area=region_bounds,
    agent_count=num_agents,
    objective='maximize_coverage'
)
```

## Active Inference Integration

SPACE provides spatial priors and likelihood functions for Active Inference agents:

- **Spatial Priors**: H3-based hierarchical spatial beliefs
- **Observation Models**: Spatial feature extraction for perception
- **Transition Models**: Movement dynamics in spatial environments
- **Preference Models**: Goal-directed spatial navigation

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **H3 Indexing** | ✅ Ready | Multi-resolution spatial indexing |
| **Nested Systems** | ✅ Ready | Hierarchical grid management |
| **Spatial Analysis** | ✅ Ready | Comprehensive spatial toolkit |
| **Coordinate Systems** | ✅ Ready | Multi-CRS transformations |
| **Topology** | ✅ Ready | Spatial relationship analysis |
| **Path Planning** | ✅ Ready | Navigation and routing |
| **Belief Propagation** | 🔮 Planned | Spatial belief networks |
| **Generative Models** | 🔮 Planned | Spatial prediction models |

---

This AGENTS.md documents how GEO-INFER-SPACE provides foundational spatial intelligence capabilities for the agent ecosystem.
