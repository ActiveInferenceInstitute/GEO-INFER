---
name: geo-infer-sim
description: Agent-based simulation for geospatial environments. Use when building spatial simulations, modeling agent interactions in geographic space, running Monte Carlo spatial experiments, or comparing spatial planning scenarios.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-time
  recommended:
    - geo-infer-bayes
    - geo-infer-act
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-SIM

## Instructions

### Core Capabilities

- **Agent-based modeling**: Spatial agents on grids, networks, and continuous space
- **Environment simulation**: Geographic environment state management, land use dynamics
- **Monte Carlo**: Stochastic spatial experiments with ensemble statistics
- **Scenario analysis**: What-if spatial scenario comparison and sensitivity analysis
- **Visualization**: Simulation playback, spatial animation, time-step rendering

### Key Imports

```python
from geo_infer_sim.core.simulation import SpatialSimulation
from geo_infer_sim.core.environment import GeoEnvironment
from geo_infer_sim.core.scenario import ScenarioManager
from geo_infer_sim.core.monte_carlo import MonteCarloRunner
```

## Examples

```python
from geo_infer_sim.core.simulation import SpatialSimulation

sim = SpatialSimulation(
    grid_size=(100, 100),
    n_agents=50,
    time_steps=200
)
sim.add_rule("diffusion", rate=0.1)
results = sim.run()
final_state = results.get_snapshot(t=200)
```

## Guidelines

- Mesa integration in development (Alpha)

### Integrations

- Integrates with AGENT for Active Inference agent behavior
- Integrates with ANT for swarm simulation
- Test: `uv run python -m pytest GEO-INFER-SIM/tests/ -v`
