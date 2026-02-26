---
name: geo-infer-ant
description: Ant Colony Optimization and swarm intelligence for geospatial problems. Use when solving spatial optimization with ACO, PSO, ABC algorithms, implementing stigmergic coordination, or optimizing geographic routing and resource allocation with bio-inspired methods.
prerequisites:
  required:
    - geo-infer-space
  recommended:
    - geo-infer-math
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-ANT

## Instructions

### Core Capabilities

- **ACO**: Ant Colony Optimization for spatial routing and TSP
- **PSO**: Particle Swarm Optimization for continuous spatial problems
- **ABC**: Artificial Bee Colony for facility location optimization
- **Stigmergy**: Pheromone-based coordination on spatial grids
- **Colony convergence**: Iteration tracking, solution quality metrics

### Key Imports

```python
from geo_infer_ant.core.aco import AntColonyOptimizer
from geo_infer_ant.core.pso import ParticleSwarmOptimizer
from geo_infer_ant.core.abc import ArtificialBeeColony
from geo_infer_ant.core.pheromone import PheromoneGrid
```

## Examples

```python
from geo_infer_ant.core.aco import AntColonyOptimizer

optimizer = AntColonyOptimizer(
    n_ants=50, alpha=1.0, beta=2.0, rho=0.5
)
best_route = optimizer.solve(distance_matrix, n_iterations=100)
print(f"Best route cost: {best_route.cost}")
```

## Guidelines

- Tests have long runtime (~213s) due to convergence iterations
- Convergence verification in development (Alpha)

### Integrations

- Integrates with AGENT for multi-agent swarm coordination
- Test: `uv run python -m pytest GEO-INFER-ANT/tests/ -v`
