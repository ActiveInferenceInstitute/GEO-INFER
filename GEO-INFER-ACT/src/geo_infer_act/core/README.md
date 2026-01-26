# core

## Overview

This directory contains core Active Inference components implementing the mathematical foundations of the Free Energy Principle. It includes 8 Python modules providing essential classes for belief updating, policy selection, free energy calculation, and generative modeling.

## Components

### active_inference.py

Main Active Inference model implementation. Provides the `ActiveInferenceModel` class that orchestrates perception (belief updating) and action (policy selection) through free energy minimization.

**Classes**: `ActiveInferenceModel`

**Key Methods**:
- `perceive(observation)`: Update beliefs based on sensory input
- `act(available_actions)`: Select action via expected free energy minimization
- `step(observation, available_actions)`: Complete perception-action cycle

### belief_updating.py

Belief updating for Active Inference models.

**Classes**: `BayesianBeliefUpdate`

### dynamic_causal_model.py

Dynamic Causal Modeling for Active Inference.

**Classes**: `DynamicCausalModel`

### free_energy.py

Variational free energy calculation for active inference models. Implements free energy computation for categorical and Gaussian models, providing the cost function minimized during perception and action.

**Classes**: `FreeEnergyCalculator`

**Key Methods**:
- `compute_categorical_free_energy()`: Free energy for discrete state spaces
- `compute_gaussian_free_energy()`: Free energy for continuous state spaces
- `compute_expected_free_energy()`: Expected free energy for policy evaluation

### generative_model.py

Generative Model for Active Inference.

**Classes**: `MarkovBlanket`, `HierarchicalLevel`, `GenerativeModel`

### markov_decision_process.py

Markov Decision Process modeling for Active Inference.

**Classes**: `MarkovDecisionProcess`

### policy_selection.py

Policy selection for active inference models.

**Classes**: `PolicySelector`

### variational_inference.py

Variational inference for active inference models.

**Classes**: `VariationalInference`



## Usage

```python
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator

# Create generative model
gen_model = GenerativeModel(
    model_type='categorical',
    parameters={'state_dim': 10, 'obs_dim': 5}
)

# Create active inference model
model = ActiveInferenceModel(model_type='categorical')
model.set_generative_model(gen_model)

# Perception: update beliefs
observation = np.array([0.2, 0.3, 0.4, 0.1, 0.0])
updated_beliefs = model.perceive(observation)

# Action: select policy
action = model.act()
```

## Integration

This directory provides core Active Inference functionality used by:
- Domain-specific models in `geo_infer_act.models`
- API interfaces in `geo_infer_act.api`
- Agent implementations in `geo_infer_agent`
- Integration with GEO-INFER-SPACE for spatial active inference
