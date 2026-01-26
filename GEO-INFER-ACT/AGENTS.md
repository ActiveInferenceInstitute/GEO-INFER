# GEO

-INFER-ACT: Active Inference Agents

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


This document describes the Active Inference agent implementations within the GEO-INFER-ACT module, which provides principled agent architectures based on the Free Energy Principle for intelligent geospatial decision-making.

## Implementation

 Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational and not yet implemented.

### Currently

 Implemented

- ✅ **Core Models**: `ActiveInferenceModel`, `GenerativeModel`
- ✅ **Inference**: `VariationalInference`, `BayesianBeliefUpdate`
- ✅ **Policy Selection**: `PolicySelector`
- ✅ **Free Energy**: `FreeEnergyCalculator`
- ✅ **Specialized Models**: `EcologicalModel`, `UrbanModel`, `ClimateModel`, `MultiAgentModel`
- ✅ **Analysis**: `ActiveInferenceAnalyzer`

### Aspirational

/Planned Features

- 🔮 **Spatial Navigation**: Spatial navigation agent implementations
- 🔮 **Model Learning**: Automated model learning from experience
- 🔮 **Spatial Belief Propagation**: Belief propagation across spatial networks

## Technical

 Capabilities

### Core

 Classes

#### Active

 Inference Models

- **`ActiveInferenceModel`**: `ActiveInferenceModel(model_type: str = "categorical", **kwargs)`
  - Main class for active inference agents
  - Methods:
    - `set_generative_model(model: GenerativeModel) -> None`
    - `perceive(observation: np.ndarray) -> np.ndarray`
    - `act(available_actions: Optional[List[Any]] = None) -> Any`
    - `update_beliefs(observations: np.ndarray) -> np.ndarray`
    - `select_action() -> Any`

- **`GenerativeModel`**: `GenerativeModel(**kwargs)`
  - Probabilistic generative model for active inference
  - Components: A (likelihood), B (transitions), C (preferences), D (priors)

- **`MarkovBlanket`**: `MarkovBlanket(**kwargs)`
  - Markov blanket architecture

- **`HierarchicalLevel`**: `HierarchicalLevel(**kwargs)`
  - Hierarchical level in nested active inference models

#### Inference

 Components

- **`VariationalInference`**: `VariationalInference(**kwargs)`
  - Variational inference for belief updating

- **`BayesianBeliefUpdate`**: `BayesianBeliefUpdate(**kwargs)`
  - Bayesian belief updating methods

- **`FreeEnergyCalculator`**: `FreeEnergyCalculator(**kwargs)`
  - Calculates variational and expected free energy
  - Methods:
    - `calculate_free_energy(beliefs, observations, generative_model) -> float`
    - `calculate_expected_free_energy(policies, beliefs, generative_model) -> np.ndarray`

#### Policy

 Selection

- **`PolicySelector`**: `PolicySelector(**kwargs)`
  - Policy selection via expected free energy minimization
  - Methods:
    - `select_policy(policies, beliefs, generative_model) -> int`
    - `calculate_expected_free_energy(policies, beliefs) -> np.ndarray`

#### Decision

 Process

- **`MarkovDecisionProcess`**: `MarkovDecisionProcess(**kwargs)`
  - MDP framework for active inference

- **`DynamicCausalModel`**: `DynamicCausalModel(**kwargs)`
  - Dynamic causal modeling for generative models

## Active

 Inference Agent Architecture

### 🤖 Module Agent Capabilities

This module provides **Core Active Inference Intelligence** for the GEO-INFER Multi-Agent System. It implements the "Brain" of the agents.

### Framework Capabilities

| Capability | Description | Status |
| :--- | :--- | :--- |
| **ActiveInferenceModel** | Core probabilistic engine minimizing free energy | ✅ Implemented |
| **GenerativeModel** | Hierarchical, factorized probabilistic models (A, B, C, D) | ✅ Implemented |
| **Policy Selection** | Expected Free Energy (EFE) minimization implementation | ✅ Implemented |
| **Spatial Navigation** | H3-integrated spatial active inference | 🔮 Planned |
| **Hierarchical Modeling** | Nested temporal scales and deep temporal models | ✅ Beta |
| **ClimateModel** | Specialized agent for climate adaptation | ✅ Implemented |
| **EcologicalModel** | Ecological niche modeling | ✅ Implemented |
| **UrbanModel** | Urban planning multi-agent simulation | ✅ Implemented |

## 🔌 Integration Patterns

### Using

 GEO-INFER-ACT in Agents

```python
from geo_infer_act import ActiveInferenceModel, ClimateModel

# 1
. Initialize a domain-specific agent
climate_agent = ClimateModel(config={'prior_precision': 2.0})

# 2
. Perceive environment (updates beliefs using free energy)
# Observations
: [Thermometer_Index, CO2_Sensor_Index]
beliefs = climate_agent.perceive([0, 1]) # 0=Normal Temp, 1=Warning CO2

# 3
. Act on environment (selects policy via EFE)
action = climate_agent.act() 
# Returns
 action index (e.g., 1=ReduceEmissions)

print(f"Agent chose action {action} to minimize expected free energy")
```

### Custom

 Generative Models

You can define custom matrices (A, B, C, D) for bespoke agents:

```python
from geo_infer_act import ActiveInferenceModel

# Define
 state-space matrices
A = ... # Likelihood P(o|s)
B = ... # Transition P(s'|s,u)
C = ... # Preferences P(o)
D = ... # Priors P(s)

agent = ActiveInferenceModel(
    model_type='categorical',
    A=A, B=B, C=C, D=D
)
```

### Structure of Core Agent

**Location**: `src/geo_infer_act/core/active_inference.py`

Active Inference agents minimize variational free energy through perception and action to maintain adaptive homeostasis with complex geospatial environments.

```python
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel

# Create
 an Active Inference model for geospatial analysis
model = ActiveInferenceModel(
    model_type='categorical',
    state_dim=10,
    obs_dim=5
)

# Set
 generative model
generative_model = GenerativeModel(
    model_type='categorical',
    parameters={
        'state_dim': 10,
        'obs_dim': 5,
        'prior_precision': 1.0
    }
)

model.set_generative_model(generative_model)

# Update
 beliefs with observations
observations = np.array([0.2, 0.3, 0.4, 0.1, 0.0])
model.update_beliefs(observations)

# Select
 policy/action
selected_policy = model.select_policy()
```

### Generative Model Architecture

**Location**: `src/geo_infer_act/core/generative_model.py`

The generative model defines how agents believe their sensory inputs are generated from hidden environmental states.

```python
from geo_infer_act.core.generative_model import GenerativeModel

# Define
 generative model for spatial-temporal dynamics
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

# The
 generative model maintains:
# - Beliefs about states
# - Preferences (prior preferences over outcomes)
# - Transition model (state evolution)
# - Observation model (how states generate observations)
```

## Perception

 and Belief Updating

### Variational

 Inference for Perception

**Location**: `src/geo_infer_act/core/variational_inference.py`

```python
from geo_infer_act.core.variational_inference import VariationalInference

# Initialize
 variational inference system
variational = VariationalInference(
    max_iterations=100,
    tolerance=1e-6
)

# Perform
 mean-field variational update
import numpy as np

prior = {'concentration': np.array([1.0, 1.0, 1.0])}  # Dirichlet prior
likelihood = {'probs': np.array([0.3, 0.4, 0.3])}    # Likelihood parameters
observations = np.array([1, 0, 0])  # Observed category

posterior = variational.mean_field_update(
    prior=prior,
    likelihood=likelihood,
    observations=observations
)

# Use
 variational inference with an ActiveInferenceModel
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
obs = np.array([0.2, 0.3, 0.4, 0.1, 0.0])

# Update
 beliefs (uses variational inference internally)
model.update_beliefs(obs)

# The
 model's belief_updater uses VariationalInference internally
```

### Belief

 Propagation in Spatial Networks 🔮

**Status**: Planned/Aspirational

**Note**: Spatial belief propagation functionality is planned for future implementation. Currently, use `GenerativeModel` with hierarchical modeling enabled for spatial reasoning.

```python
# 🔮 Planned implementation - not yet available
# from
 geo_infer_act.core.belief_propagation import SpatialBeliefPropagation

# Currently
, use GenerativeModel with spatial mode:
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

# Use
 the model's belief updating for spatial reasoning
# See
 belief_updating.py for BayesianBeliefUpdate
```

## Action

 Selection and Planning

### Expected

 Free Energy Minimization

**Location**: `src/geo_infer_act/core/policy_selection.py`

```python
from geo_infer_act.core.policy_selection import PolicySelector

# Initialize
 policy selector
policy_selector = PolicySelector(temperature=1.0)

# Use
 with ActiveInferenceModel
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
model.update_beliefs(np.array([0.2, 0.3, 0.4, 0.1, 0.0]))

# Select
 policy (uses PolicySelector internally)
selected_policy = model.select_policy()

# Or
 use PolicySelector directly with policies
import numpy as np

beliefs = np.array([0.3, 0.4, 0.3])  # Current beliefs
policies = [
    {'action': 'move_north', 'expected_outcome': np.array([0.2, 0.5, 0.3])},
    {'action': 'move_south', 'expected_outcome': np.array([0.4, 0.3, 0.3])},
    {'action': 'stay', 'expected_outcome': np.array([0.3, 0.4, 0.3])}
]

selected = policy_selector.select_policy(beliefs, policies)
```

### Spatial

 Navigation and Sampling 🔮

**Status**: Planned/Aspirational

**Note**: Spatial navigation agent functionality is planned for future implementation. Currently, use `ActiveInferenceModel` with spatial extensions for spatial reasoning.

```python
# 🔮 Planned implementation - not yet available
# from
 geo_infer_act.models.spatial_navigation import SpatialNavigationAgent

# Currently
, use ActiveInferenceModel with spatial considerations:
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

## Learning

 and Adaptation

### Model

 Learning from Experience 🔮

**Status**: Planned/Aspirational

**Note**: Model learning functionality is planned for future implementation. Currently, use `GenerativeModel` with manual parameter updates.

```python
# 🔮 Planned implementation - not yet available
# from
 geo_infer_act.core.model_learning import ActiveInferenceLearner

# Currently
, use GenerativeModel and update parameters manually:
from geo_infer_act.core.generative_model import GenerativeModel

generative_model = GenerativeModel(
    model_type='categorical',
    parameters={
        'state_dim': 10,
        'obs_dim': 5,
        'prior_precision': 1.0
    }
)

# Update
 model parameters based on experience
# The
 model's transition_model and observation_model can be updated
# based
 on collected experience data
```

## Multi

-Agent Active Inference

### Agent

 Coordination Frameworks

**Location**: `src/geo_infer_act/models/multi_agent.py`

```python
from geo_infer_act.models.multi_agent import MultiAgentModel

# Create
 multi-agent coordination system
multi_agent_system = MultiAgentModel(
    model_type='categorical',
    num_agents=3,
    shared_beliefs=True
)

# Establish
 agent communication network
communication_network = multi_agent_system.establish_communication(
    spatial_connectivity=communication_ranges,
    bandwidth_constraints=channel_capacity,
    reliability_requirements=mission_critical
)

# Coordinate
 beliefs across agents
consensus_beliefs = multi_agent_system.coordinate_beliefs(
    individual_beliefs=agent_posteriors,
    communication_graph=network_topology,
    consensus_algorithm='belief_propagation',
    convergence_threshold=0.01
)

# Plan
 coordinated actions
coordinated_actions = multi_agent_system.plan_coordinated_actions(
    shared_beliefs=consensus_beliefs,
    individual_goals=agent_objectives,
    resource_constraints=shared_resources,
    conflict_resolution='pareto_optimal'
)
```

## Specialized

 Agent Types

### Ecological

 Monitoring Agents

**Location**: `src/geo_infer_act/models/ecological.py`

```python
from geo_infer_act.models.ecological import EcologicalModel

# Create
 ecological model for active inference
eco_model = EcologicalModel(config={
    'state_dim': 10,
    'obs_dim': 5,
    'prior_precision': 1.0
})

# Use
 the model for ecological monitoring
# The
 model extends ActiveInferenceModel and can be used
# for
 ecological state inference and prediction

# Step through model evolution
# Needs observation: [Food_Signal, Threat_Signal]
obs = [2, 0] # Abundant food, no threat
result = eco_model.step(observation=obs)

# Use
 with ActiveInferenceModel interface
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
# Integrate
 ecological model for domain-specific reasoning
```

### Urban

 Planning Agents

**Location**: `src/geo_infer_act/models/urban.py`

```python
from geo_infer_act.models.urban import UrbanModel

# Create
 urban planning model
urban_model = UrbanModel(
    config=None,
    n_agents=3,      # Number of stakeholder agents
    n_resources=4,   # Number of resource types
    n_locations=5,   # Number of spatial locations
    planning_horizon=10  # Planning horizon
)

# Step
 through urban planning process
result = urban_model.step(actions=None)

# Use
 the model for urban planning with active inference
# The
 model extends ActiveInferenceModel and provides
# urban
-specific modeling capabilities
```

### Climate

 Adaptation Agents

**Location**: `src/geo_infer_act/models/climate.py`

```python
from geo_infer_act.models.climate import ClimateModel

# Create
 climate adaptation model
climate_model = ClimateModel(config={
    'state_dim': 10,
    'obs_dim': 5,
    'prior_precision': 1.0
})

# Use
 the model for climate adaptation planning
# The
 model extends ActiveInferenceModel and can be used
# for
 climate vulnerability assessment and adaptation planning

# Step through climate model evolution
# Needs observation: [Thermometer, CO2_Sensor]
obs = [1, 1] # Elevated temp, Warning CO2
# Returns tuple (beliefs, action)
beliefs, action = climate_model.step(observation=obs)

# Use
 with ActiveInferenceModel for climate adaptation reasoning
from geo_infer_act.core.active_inference import ActiveInferenceModel

model = ActiveInferenceModel(model_type='categorical')
# Integrate
 climate model for domain-specific reasoning
```

## Agent

 Performance Evaluation

### Free Energy Analysis

**Location**: `src/geo_infer_act/utils/analysis.py`

```python
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer

# Initialize
 performance analysis
analyzer = ActiveInferenceAnalyzer(
    model=None,  # ActiveInferenceModel to analyze
    history=None  # History of model states
)

# Analyze
 agent/model performance
# The
 analyzer provides methods to analyze:
# - Belief trajectories
# - Free energy dynamics
# - Policy selection patterns
# - Learning progress

# Use
 with model history
analyzer.model = active_inference_model
analyzer.history = model_history

# Analyze
 performance
analysis_results = analyzer.analyze()

# The
 analyzer provides various analysis methods
# See
 ActiveInferenceAnalyzer class for full API
```

---

## Complete

 API Reference

### Core

 Classes

#### `ActiveInferenceModel`

**Location**: `src/geo_infer_act/core/active_inference.py`

Main class for active inference agents with support for nested models.

**Key Methods**:

- `__init__(model_type: str = "categorical", **kwargs)`: Initialize an Active Inference model
- `set_generative_model(model: GenerativeModel)`: Set the generative model
- `perceive(observation: np.ndarray) -> np.ndarray`: Update beliefs based on new observation
- `act(available_actions: Optional[List[Any]] = None) -> Any`: Select action based on expected free energy minimization
- `step(observation: np.ndarray, available_actions: Optional[List[Any]] = None) -> Tuple[np.ndarray, Any]`: Perform one complete active inference step
- `compute_free_energy() -> float`: Compute current variational free energy
- `reset()`: Reset the model to initial state
- `get_history() -> List[Dict[str, Any]]`: Get the complete history of interactions
- `get_current_state() -> Dict[str, Any]`: Get current model state

#### GenerativeModel Class

**Location**: `src/geo_infer_act/core/generative_model.py`

Generative model implementation for active inference supporting hierarchical architectures, Markov blankets, and spatial extensions.

**Key Methods**:

- `__init__(model_type: str, parameters: Dict[str, Any], model_id: Optional[str] = None)`: Initialize a generative model
- `update_beliefs(observations: Dict[str, np.ndarray]) -> Dict[str, Any]`: Update beliefs using hierarchical inference
- `compute_free_energy() -> float`: Compute variational free energy
- `add_nested_level(child_model: 'GenerativeModel')`: Add a nested child model
- `enable_h3_spatial(h3_resolution: int, boundary: Dict[str, Any])`: Enable H3-based spatial modeling
- `set_preferences(preferences: Dict[str, np.ndarray]) -> None`: Set prior preferences with hierarchical support

#### `FreeEnergyCalculator`

**Location**: `src/geo_infer_act/core/free_energy.py`

Calculator for variational free energy in active inference models.

**Key Methods**:

- `compute_categorical_free_energy(beliefs: np.ndarray, observations: np.ndarray, preferences: Optional[np.ndarray] = None) -> float`: Compute variational free energy for categorical models
- `compute_gaussian_free_energy(mean: np.ndarray, precision: np.ndarray, observations: np.ndarray, prior_mean: Optional[np.ndarray] = None, prior_precision: Optional[np.ndarray] = None) -> float`: Compute free energy for Gaussian models
- `compute_expected_free_energy(beliefs: np.ndarray, policy: Dict[str, Any], preferences: Optional[np.ndarray] = None) -> float`: Compute expected free energy for policy evaluation

#### `PolicySelector`

**Location**: `src/geo_infer_act/core/policy_selection.py`

Policy selector for active inference models based on expected free energy minimization.

**Key Methods**:

- `select_policy(beliefs: np.ndarray, policies: List[Dict[str, Any]], preferences: Optional[np.ndarray] = None) -> Dict[str, Any]`: Select a policy based on expected free energy
- `compute_expected_free_energy(beliefs: np.ndarray, policy: Dict[str, Any], preferences: Optional[np.ndarray] = None) -> float`: Compute expected free energy for a policy
- `select_action(beliefs: np.ndarray, available_actions: List[Any], generative_model: Any) -> Any`: Select a single action based on current beliefs

#### `BayesianBeliefUpdate`

**Location**: `src/geo_infer_act/core/belief_updating.py`

Bayesian belief updating for active inference models.

**Key Methods**:

- `update_categorical(prior_beliefs: np.ndarray, observation: np.ndarray, likelihood_matrix: np.ndarray) -> np.ndarray`: Update categorical beliefs using Bayes' rule
- `update_gaussian(prior_mean: np.ndarray, prior_precision: np.ndarray, observation: np.ndarray, observation_matrix: np.ndarray, observation_precision: np.ndarray) -> Dict[str, np.ndarray]`: Update Gaussian beliefs using Kalman filter equations
- `compute_prediction_error(prediction: np.ndarray, observation: np.ndarray, precision: float) -> float`: Compute precision-weighted prediction error

### Domain

 Models

#### `EcologicalModel`

**Location**: `src/geo_infer_act/models/ecological.py`

Ecological niche modeling using Active Inference. Simulates organism adaptation to ecological niches.

**Key Methods**:

- `__init__(config: Dict[str, Any] = None)`: Initialize the Ecological Model
- `step(observation: List[int])`: Advance the ecological model by one step

#### `ClimateModel`

**Location**: `src/geo_infer_act/models/climate.py`

Climate adaptation modeling using Active Inference.

**Key Methods**:

- `step(observations)`: Execute one step of active inference

#### `UrbanModel`

**Location**: `src/geo_infer_act/models/urban.py`

Urban planning model using active inference.

**Key Methods**:

- `step(input_actions)`: Advance one simulation step
- `run_simulation(n_steps: int)`: Run complete simulation

#### `MultiAgentModel`

**Location**: `src/geo_infer_act/models/multi_agent.py`

Multi-agent coordination using active inference.

**Key Methods**:

- `step(actions: Optional[List[Dict[str, Any]]]) -> Tuple[Dict[str, Any], bool]`: Advance multi-agent system
- `enable_h3_spatial(resolution: int, boundary: Dict[str, Any])`: Enable H3 spatial modeling
- `coordinate_agents() -> Dict[str, Any]`: Coordinate agents through message passing

### Utility Helper Classes

#### `ActiveInferenceAnalyzer`

**Location**: `src/geo_infer_act/utils/analysis.py`

Comprehensive analyzer for Active Inference model behavior.

**Key Methods**:

- `record_step(beliefs, observations, actions, policies, free_energy, metrics, timestamp)`: Record a single Active Inference step
- `analyze_perception_patterns() -> Dict[str, Any]`: Analyze perception patterns
- `analyze_action_selection_patterns() -> Dict[str, Any]`: Analyze action selection patterns
- `analyze_free_energy_patterns() -> Dict[str, Any]`: Analyze free energy patterns
- `generate_comprehensive_report() -> str`: Generate analysis report

### Math Utility Functions

**Location**: `src/geo_infer_act/utils/math.py`

Mathematical utilities for active inference:

- `softmax(x: np.ndarray, temperature: float = 1.0, axis: int = -1) -> np.ndarray`: Compute softmax transformation
- `kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float`: Compute Kullback-Leibler divergence
- `entropy(p: np.ndarray, base: Union[float, str] = 'e') -> float`: Compute entropy of probability distribution
- `compute_free_energy_categorical(beliefs: np.ndarray, observations: np.ndarray, prior: Optional[np.ndarray] = None) -> float`: Compute variational free energy for categorical models

---

This AGENTS.md file documents the Active Inference agent architectures, perception-action cycles, learning mechanisms, and specialized applications within the GEO-INFER-ACT module. The framework provides principled, mathematically grounded approaches to intelligent agent design for complex geospatial decision-making.
