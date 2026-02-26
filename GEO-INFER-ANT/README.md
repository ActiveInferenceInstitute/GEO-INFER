---
title: "GEO-INFER-ANT: Swarm Intelligence"
description: "Ant colony optimization, swarm coordination, and collective behavior"
purpose: "Enable swarm-based problem solving and agent coordination"
module_type: "Core Intelligence"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "ACT"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-ACT", "GEO-INFER-AGENT"]
tags: ["swarm", "ant-colony", "optimization", "collective", "coordination"]
difficulty: "Advanced"
estimated_time: "40"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> |
  <a href="../README.md#-module-overview">Module Index</a> |
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-ANT: Swarm Intelligence

## Overview

**GEO-INFER-ANT** provides swarm intelligence algorithms for geospatial optimization problems, including ant colony optimization (ACO), stigmergy-based coordination, pheromone field dynamics, and collective decision-making. These bio-inspired approaches solve combinatorial optimization problems such as vehicle routing, resource allocation, and spatial coverage by simulating the decentralized coordination observed in social insect colonies.

## Core Objectives

- **Scalable Route Optimization**: Solve TSP, VRP, and multi-depot routing using ant colony optimization with configurable colony parameters (alpha, beta, evaporation rate)
- **Stigmergic Coordination**: Enable indirect agent communication through pheromone fields mapped onto H3 hexagonal grids for spatial decision-making
- **Collective Intelligence**: Aggregate individual agent observations into emergent group-level solutions without centralized control
- **Geospatial Integration**: Operate natively on H3 cell grids, GeoDataFrames, and network graphs for real-world spatial optimization

## Features

### Ant Colony Optimization

```python
from geo_infer_ant import AntColonyOptimizer

# Solve TSP with ACO
aco = AntColonyOptimizer()

solution = aco.solve(
    problem="tsp",
    nodes=delivery_points,
    n_ants=50
)

print(f"Best route: {solution.distance}")
```

### Swarm Coordination

```python
from geo_infer_ant import SwarmCoordinator

# Coordinate drone swarm
swarm = SwarmCoordinator()

swarm.deploy(
    agents=drones,
    area=search_region,
    behavior="coverage"
)
```

### Pheromone Mapping

```python
from geo_infer_ant import PheromoneMapper

# Map pheromone trails
mapper = PheromoneMapper()

map = mapper.create(
    paths=agent_paths,
    decay_rate=0.1
)
```

### Collective Decision

```python
from geo_infer_ant import CollectiveDecision

# Swarm voting
decision = CollectiveDecision()

result = decision.vote(
    agents=swarm,
    alternatives=options
)
```

## API Reference

| Class / Function | Description |
|------------------|-------------|
| `AntColony(n_ants, n_iterations, alpha, beta, evaporation_rate)` | Core ACO solver for combinatorial optimization on distance/cost matrices |
| `StigmergyMap(cells)` | Pheromone field on H3 cells with deposit, evaporate, and diffuse operations |
| `PheromoneField(grid_shape, decay_rate)` | Grid-based pheromone dynamics with time-stepped evaporation |
| `SwarmCoordinator(agents, behavior)` | Multi-agent deployment and spatial coverage coordinator |
| `CollectiveDecision(method)` | Weighted swarm voting and quorum-based group decision |
| `AntColonyOptimizer.solve(distances)` | Returns `(best_path, best_distance)` for a given distance matrix |
| `StigmergyMap.deposit(cell, amount)` | Deposits pheromone at a specific H3 cell |
| `StigmergyMap.get_concentration(cell)` | Reads current pheromone level at a cell |

## Algorithms

| Algorithm | Application |
|-----------|-------------|
| **ACO** | Routing, scheduling |
| **PSO** | Optimization |
| **Bees** | Foraging patterns |

## Working Code Examples

### Example 1: Basic ACO Route Optimization

```python
from geo_infer_ant.core.ant_colony import AntColony
import numpy as np

# Create distance matrix for 5 locations
distances = np.array([[0, 2, 9, 10, 5],
                       [2, 0, 7, 8, 3],
                       [9, 7, 0, 4, 6],
                       [10, 8, 4, 0, 1],
                       [5, 3, 6, 1, 0]])

colony = AntColony(n_ants=20, n_iterations=100, alpha=1.0, beta=2.0, evaporation_rate=0.1)
best_path, best_distance = colony.solve(distances)
print(f"Best path: {best_path}, Distance: {best_distance:.2f}")
```

### Example 2: Pheromone Field on H3 Grid

```python
from geo_infer_ant.core.stigmergy import StigmergyMap
import h3

# Create pheromone field on H3 cells
cells = [h3.latlng_to_cell(47.6 + i*0.01, -122.3 + i*0.01, 9) for i in range(5)]
field = StigmergyMap(cells)
field.deposit(cells[0], amount=10.0)
field.evaporate(rate=0.05)
print(f"Concentration at cell 0: {field.get_concentration(cells[0]):.3f}")
```

## Integration

GEO-INFER-ANT integrates with the following modules:

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-SPACE** | ANT <-- SPACE | H3 hexagonal grid cells used as pheromone field substrate |
| **GEO-INFER-MATH** | ANT <-- MATH | Graph algorithms and distance computations for ACO solvers |
| **GEO-INFER-TRANSPORT** | ANT --> TRANSPORT | Optimized routes fed into transport network analysis |
| **GEO-INFER-ACT** | ANT <-> ACT | Active inference agents use swarm signals; swarm uses free energy for exploration |
| **GEO-INFER-AGENT** | ANT --> AGENT | Swarm behaviors composed into multi-agent systems |

Data flow: SPACE/MATH provide spatial grids and graph structures. ANT runs optimization. Results flow to TRANSPORT and AGENT for operational use.

## Installation

```bash
uv pip install -e "./GEO-INFER-ANT"
```

## Testing

```bash
# Run all ANT tests
uv run python -m pytest GEO-INFER-ANT/tests/ -v

# Run unit tests only
uv run python -m pytest GEO-INFER-ANT/tests/unit/ -v

# Run with coverage
uv run python -m pytest GEO-INFER-ANT/tests/ --cov=GEO-INFER-ANT/src --cov-report=html
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

**Status**: Alpha

**Last Updated**: 2026-02-25
