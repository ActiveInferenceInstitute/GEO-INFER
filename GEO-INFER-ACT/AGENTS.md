# GEO-INFER-ACT: Active Inference Agents

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---


## Overview

This document describes the Active Inference agent implementations within the GEO-INFER-ACT module, which provides principled agent architectures based on the Free Energy Principle for intelligent geospatial decision-making.

## Implementation Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational and not yet implemented.

### Currently Implemented

- ✅ **Core Models**: `ActiveInferenceModel`, `GenerativeModel`
- ✅ **Inference**: `VariationalInference`, `BayesianBeliefUpdate`
- ✅ **Policy Selection**: `PolicySelector`
- ✅ **Specialized Models**: `EcologicalModel`, `UrbanModel`, `ClimateModel`, `MultiAgentModel`
- ✅ **Analysis**: `ActiveInferenceAnalyzer`

### Aspirational/Planned Features

- 🔮 **Spatial Navigation**: Spatial navigation agent implementations
- 🔮 **Model Learning**: Automated model learning from experience
- 🔮 **Spatial Belief Propagation**: Belief propagation across spatial networks

## Active Inference Agent Architecture

### 🤖 Module Agent Capabilities

This module provides **Core Active Inference Intelligence** for the GEO-INFER Multi-Agent System. It implements the "Brain" of the agents.

### Framework Capabilities
| Capability | Description | Status |
|------------|-------------|--------|
| **ActiveInferenceModel** | Core probabilistic engine minimizing free energy | ✅ Real |
| **GenerativeModel** | Hierarchical, factorized probabilistic models (A, B, C, D) | ✅ Real |
| **Policy Selection** | Expected Free Energy (EFE) minimization implementation | ✅ Real |
| **Spatial Navigation** | H3-integrated spatial active inference | ✅ Beta |
| **Hierarchical Modeling** | Nested temporal scales and deep temporal models | ✅ Beta |
| **ClimateModel** | Specialized agent for climate adaptation | ✅ Real |
| **EcologicalModel** | Ecological niche modeling | 🟡 Alpha |

## 🔌 Integration Patterns

### Using GEO-INFER-ACT in Agents

```python
from geo_infer_act import ActiveInferenceModel, ClimateModel

# 1. Initialize a domain-specific agent (Real Pymdp Implementation)
climate_agent = ClimateModel(config={'prior_precision': 2.0})

# 2. Perceive environment (updates beliefs using free energy)
# Observations: [Thermometer_Index, CO2_Sensor_Index]
beliefs = climate_agent.perceive([0, 1]) # 0=Normal Temp, 1=Warning CO2

# 3. Act on environment (selects policy via EFE)
action = climate_agent.act() 
# Returns action index (e.g., 1=ReduceEmissions)

print(f"Agent chose action {action} to minimize expected free energy")
```

### Advanced Usage: Custom Generative Models

You can define custom matrices (A, B, C, D) for bespoke agents:

```python
from geo_infer_act import ActiveInferenceModel

# Define state-space matrices
A = ... # Likelihood P(o|s)
B = ... # Transition P(s'|s,u)
C = ... # Preferences P(o)
D = ... # Priors P(s)

agent = ActiveInferenceModel(
    model_type='categorical',
    A=A, B=B, C=C, D=D
)
```

### Core Agent Structure

**Location**: `src/geo_infer_act/core/active_inference.py`

Active Inference agents minimize variational free energy through perception and action to maintain adaptive homeostasis with complex geospatial environments.

```python
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel

# Create an Active Inference model for geospatial analysis
model = ActiveInferenceModel(
    model_type='categorical',
    state_dim=10,
    obs_dim=5
)

# Set generative model
generative_model = GenerativeModel(
    model_type='categorical',
    parameters={
        'state_dim': 10,
        'obs_dim': 5,
        'prior_precision': 1.0
    }
)

model.set_generative_model(generative_model)

# Update beliefs with observations
observations = np.array([0.2, 0.3, 0.4, 0.1, 0.0])
model.update_beliefs(observations)

# Select policy/action
selected_policy = model.select_policy()
```

### Generative Model Structure

**Location**: `src/geo_infer_act/core/generative_model.py`

The generative model defines how agents believe their sensory inputs are generated from hidden environmental states.

```python
from geo_infer_act.core.generative_model import GenerativeModel

# Define generative model for spatial-temporal dynamics
generative_model = GenerativeModel(
    model_type='categorical',  # or 'gaussian', 'mixed'
    parameters={
        'state_dim': 10,      # Dimensionality of state space
        'obs_dim': 5,         # Dimensionality of observation space
        'prior_precision': 1.0,
        'hierarchical': True,  # Enable hierarchical modeling
        'spatial_mode': True   # Enable spatial extensions
    }
)

# The generative model maintains:
# - Beliefs about states
# - Preferences (prior preferences over outcomes)
# - Transition model (state evolution)
# - Observation model (how states generate observations)
```

## Perception and Belief Updating

### Variational Inference for Perception

**Location**: `src/geo_infer_act/core/variational_inference.py`

```python
from geo_infer_act.core.variational_inference import VariationalInference

# Initialize variational inference system
variational = VariationalInference(
    max_iterations=100,
    tolerance=1e-6
)

# Perform mean-field variational update
import numpy as np

prior = {'concentration': np.array([1.0, 1.0, 1.0])}  # Dirichlet prior
likelihood = {'probs': np.array([0.3, 0.4, 0.3])}    # Likelihood parameters
observations = np.array([1, 0, 0])  # Observed category

posterior = variational.mean_field_update(
    prior=prior,
    likelihood=likelihood,
    observations=observations
)

# Use variational inference with an ActiveInferenceModel
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
obs = np.array([0.2, 0.3, 0.4, 0.1, 0.0])

# Update beliefs (uses variational inference internally)
model.update_beliefs(obs)

# The model's belief_updater uses VariationalInference internally
```

### Belief Propagation in Spatial Networks 🔮

**Status**: Planned/Aspirational

**Note**: Spatial belief propagation functionality is planned for future implementation. Currently, use `GenerativeModel` with hierarchical modeling enabled for spatial reasoning.

```python
# 🔮 Planned implementation - not yet available
# from geo_infer_act.core.belief_propagation import SpatialBeliefPropagation

# Currently, use GenerativeModel with spatial mode:
from geo_infer_act.core.generative_model import GenerativeModel

generative_model = GenerativeModel(
    model_type='categorical',
    parameters={
        'state_dim': 10,
        'obs_dim': 5,
        'spatial_mode': True,  # Enable spatial extensions
        'hierarchical': True   # Enable hierarchical modeling
    }
)

# Use the model's belief updating for spatial reasoning
# See belief_updating.py for BayesianBeliefUpdate
```

## Action Selection and Planning

### Expected Free Energy Minimization

**Location**: `src/geo_infer_act/core/policy_selection.py`

```python
from geo_infer_act.core.policy_selection import PolicySelector

# Initialize policy selector
policy_selector = PolicySelector(temperature=1.0)

# Use with ActiveInferenceModel
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
model.update_beliefs(np.array([0.2, 0.3, 0.4, 0.1, 0.0]))

# Select policy (uses PolicySelector internally)
selected_policy = model.select_policy()

# Or use PolicySelector directly with policies
import numpy as np

beliefs = np.array([0.3, 0.4, 0.3])  # Current beliefs
policies = [
    {'action': 'move_north', 'expected_outcome': np.array([0.2, 0.5, 0.3])},
    {'action': 'move_south', 'expected_outcome': np.array([0.4, 0.3, 0.3])},
    {'action': 'stay', 'expected_outcome': np.array([0.3, 0.4, 0.3])}
]

selected = policy_selector.select_policy(beliefs, policies)
```

### Spatial Navigation and Sampling 🔮

**Status**: Planned/Aspirational

**Note**: Spatial navigation agent functionality is planned for future implementation. Currently, use `ActiveInferenceModel` with spatial extensions for spatial reasoning.

```python
# 🔮 Planned implementation - not yet available
# from geo_infer_act.models.spatial_navigation import SpatialNavigationAgent

# Currently, use ActiveInferenceModel with spatial considerations:
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel

model = ActiveInferenceModel(model_type='categorical')
generative_model = GenerativeModel(
    model_type='categorical',
    parameters={
        'state_dim': 10,
        'obs_dim': 5,
        'spatial_mode': True  # Enable spatial extensions
    }
)
model.set_generative_model(generative_model)
```

## Learning and Adaptation

### Model Learning from Experience 🔮

**Status**: Planned/Aspirational

**Note**: Model learning functionality is planned for future implementation. Currently, use `GenerativeModel` with manual parameter updates.

```python
# 🔮 Planned implementation - not yet available
# from geo_infer_act.core.model_learning import ActiveInferenceLearner

# Currently, use GenerativeModel and update parameters manually:
from geo_infer_act.core.generative_model import GenerativeModel

generative_model = GenerativeModel(
    model_type='categorical',
    parameters={
        'state_dim': 10,
        'obs_dim': 5,
        'prior_precision': 1.0
    }
)

# Update model parameters based on experience
# The model's transition_model and observation_model can be updated
# based on collected experience data
```

## Multi-Agent Active Inference

### Agent Coordination Frameworks

**Location**: `src/geo_infer_act/models/multi_agent.py`

```python
from geo_infer_act.models.multi_agent import MultiAgentModel

# Create multi-agent coordination system
multi_agent_system = MultiAgentModel(
    model_type='categorical',
    num_agents=3,
    shared_beliefs=True
)

# Establish agent communication network
communication_network = multi_agent_system.establish_communication(
    spatial_connectivity=communication_ranges,
    bandwidth_constraints=channel_capacity,
    reliability_requirements=mission_critical
)

# Coordinate beliefs across agents
consensus_beliefs = multi_agent_system.coordinate_beliefs(
    individual_beliefs=agent_posteriors,
    communication_graph=network_topology,
    consensus_algorithm='belief_propagation',
    convergence_threshold=0.01
)

# Plan coordinated actions
coordinated_actions = multi_agent_system.plan_coordinated_actions(
    shared_beliefs=consensus_beliefs,
    individual_goals=agent_objectives,
    resource_constraints=shared_resources,
    conflict_resolution='pareto_optimal'
)
```

## Specialized Agent Types

### Ecological Monitoring Agents

**Location**: `src/geo_infer_act/models/ecological.py`

```python
from geo_infer_act.models.ecological import EcologicalModel

# Create ecological model for active inference
eco_model = EcologicalModel(config={
    'state_dim': 10,
    'obs_dim': 5,
    'prior_precision': 1.0
})

# Use the model for ecological monitoring
# The model extends ActiveInferenceModel and can be used
# for ecological state inference and prediction

# Step through model evolution
result = eco_model.step(actions=None)

# Use with ActiveInferenceModel interface
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
# Integrate ecological model for domain-specific reasoning
```

### Urban Planning Agents

**Location**: `src/geo_infer_act/models/urban.py`

```python
from geo_infer_act.models.urban import UrbanModel

# Create urban planning model
urban_model = UrbanModel(
    config=None,
    n_agents=3,      # Number of stakeholder agents
    n_resources=4,   # Number of resource types
    n_locations=5,   # Number of spatial locations
    planning_horizon=10  # Planning horizon
)

# Step through urban planning process
result = urban_model.step(actions=None)

# Use the model for urban planning with active inference
# The model extends ActiveInferenceModel and provides
# urban-specific modeling capabilities
```

### Climate Adaptation Agents

**Location**: `src/geo_infer_act/models/climate.py`

```python
from geo_infer_act.models.climate import ClimateModel

# Create climate adaptation model
climate_model = ClimateModel(config={
    'state_dim': 10,
    'obs_dim': 5,
    'prior_precision': 1.0
})

# Use the model for climate adaptation planning
# The model extends ActiveInferenceModel and can be used
# for climate vulnerability assessment and adaptation planning

# Step through climate model evolution
result = climate_model.step(actions=None)

# Use with ActiveInferenceModel for climate adaptation reasoning
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
# Integrate climate model for domain-specific reasoning
```

## Agent Performance Evaluation

### Free Energy Analysis

**Location**: `src/geo_infer_act/utils/analysis.py`

```python
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer

# Initialize performance analysis
analyzer = ActiveInferenceAnalyzer(
    model=None,  # ActiveInferenceModel to analyze
    history=None  # History of model states
)

# Analyze agent/model performance
# The analyzer provides methods to analyze:
# - Belief trajectories
# - Free energy dynamics
# - Policy selection patterns
# - Learning progress

# Use with model history
analyzer.model = active_inference_model
analyzer.history = model_history

# Analyze performance
analysis_results = analyzer.analyze()

# The analyzer provides various analysis methods
# See ActiveInferenceAnalyzer class for full API
```

---

This AGENTS.md file documents the Active Inference agent architectures, perception-action cycles, learning mechanisms, and specialized applications within the GEO-INFER-ACT module. The framework provides principled, mathematically grounded approaches to intelligent agent design for complex geospatial decision-making.

