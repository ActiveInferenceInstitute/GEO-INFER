---
name: geo-infer-act
description: Active Inference implementation for geospatial agents. Use when implementing free energy minimization, belief updating, perception-action loops, generative models, or expected free energy computation for spatial decision-making.
prerequisites:
  required:
    - geo-infer-bayes
  recommended:
    - geo-infer-space
    - geo-infer-time
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-ACT

## Instructions

Core Active Inference module implementing the Free Energy Principle for geospatial agents.

### Core Capabilities

- **Free energy minimization**: Variational and expected free energy
- **Generative models**: Dirichlet-categorical state-space models
- **Belief updating**: Bayesian belief propagation with spatial priors
- **Perception-action loops**: Sensory prediction and policy selection
- **Precision dynamics**: Attention-weighted inference

### Key Imports

```python
from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.belief_updating import BeliefUpdater
from geo_infer_act.core.active_inference import ActiveInferenceAgent
```

## Examples

```python
from geo_infer_act.core.active_inference import ActiveInferenceAgent
import numpy as np

agent = ActiveInferenceAgent(
    n_states=4, n_observations=3, n_actions=2
)
observation = np.array([0.8, 0.1, 0.1])
action = agent.act(observation)
```

## Guidelines

- Generative models use real Dirichlet/categorical sampling (no placeholders)
- Visualization uses real matplotlib belief trajectory plotting
- Optional deps: `jax`, `tensorflow_probability` — graceful degradation if missing
- Ground all implementations in FEP mathematical principles
- Test: `uv run python -m pytest GEO-INFER-ACT/tests/ -v`

### Integrations

- **BAYES** → Shared posterior inference, generative model fitting
- **AGENT** → Active Inference perception-action loops
- **SPACE** → Spatial state spaces for geographic agents
- **COG** → Cognitive models grounded in free energy
- **SIM** → Active Inference agent simulations
