# GEO-INFER-ACT Source Code

This directory contains the core implementation of the GEO-INFER-ACT Active Inference framework for geospatial applications.

## Directory Structure

```
src/
├── geo_infer_act/
│   ├── __init__.py                    # Package initialization
│   ├── api/                          # API interfaces
│   │   ├── __init__.py
│   │   ├── client.py                 # API client
│   │   └── endpoints.py              # REST endpoints
│   ├── core/                         # Core Active Inference components
│   │   ├── __init__.py
│   │   ├── active_inference.py       # Main Active Inference implementation
│   │   ├── belief_updating.py        # Variational inference for perception
│   │   ├── dynamic_causal_model.py   # Causal modeling
│   │   ├── free_energy.py            # Free energy calculations
│   │   ├── generative_model.py       # Generative model definitions
│   │   ├── markov_decision_process.py # MDP formulations
│   │   ├── policy_selection.py       # Expected free energy minimization
│   │   └── variational_inference.py  # Variational methods
│   ├── models/                       # Specialized Active Inference models
│   │   ├── __init__.py
│   │   ├── base.py                   # Base model classes
│   │   ├── climate.py                # Climate adaptation models
│   │   ├── ecological.py             # Ecological monitoring models
│   │   ├── multi_agent.py            # Multi-agent coordination
│   │   ├── resource.py               # Resource management models
│   │   └── urban.py                  # Urban planning models
│   └── utils/                        # Utility functions and analysis
│       ├── __init__.py
│       ├── analysis.py               # Performance analysis tools
│       ├── config.py                 # Configuration management
│       ├── geospatial_ai.py          # Geospatial AI utilities
│       ├── integration.py            # Integration helpers
│       ├── math.py                   # Mathematical utilities
│       └── visualization.py          # Visualization tools
```

## Core Active Inference Implementation

### Main Active Inference Engine

**Location**: `core/active_inference.py`

The central Active Inference agent implementation:

```python
from geo_infer_act.core.active_inference import ActiveInferenceAgent

# Create an Active Inference agent
agent = ActiveInferenceAgent(
    agent_id="spatial_ai_agent",
    generative_model=spatial_generative_model,
    precision_parameters={
        'observation_precision': 1.0,
        'action_precision': 0.8,
        'state_precision': 0.6
    },
    planning_horizon=15,
    learning_rate=0.01
)

# Agent perception cycle
observations = agent.perceive_environment(sensor_data)
beliefs = agent.update_beliefs(observations)

# Agent action selection
actions = agent.select_actions(beliefs, available_actions)

# Agent learning
agent.learn_from_experience(outcomes, performance_feedback)
```

### Free Energy Calculations

**Location**: `core/free_energy.py`

Implements variational free energy and expected free energy calculations:

```python
from geo_infer_act.core.free_energy import FreeEnergyCalculator

calculator = FreeEnergyCalculator(
    temperature_parameter=1.0,
    prior_preferences=goal_prior
)

# Calculate variational free energy
vfe = calculator.variational_free_energy(
    posterior_beliefs=beliefs,
    observations=observations,
    generative_model=model
)

# Calculate expected free energy for policy evaluation
efe = calculator.expected_free_energy(
    policy=proposed_policy,
    current_beliefs=beliefs,
    generative_model=model
)
```

### Variational Inference

**Location**: `core/variational_inference.py`

Implements variational methods for approximate Bayesian inference:

```python
from geo_infer_act.core.variational_inference import VariationalInference

vi = VariationalInference(
    inference_method='amortized_vi',
    optimizer='adam',
    convergence_threshold=1e-6
)

# Perform variational inference
posterior = vi.infer_posterior(
    observations=data,
    generative_model=model,
    prior_beliefs=priors
)

# Update beliefs with new evidence
updated_beliefs = vi.update_beliefs(
    current_beliefs=previous_posterior,
    new_evidence=new_observations
)
```

### Policy Selection

**Location**: `core/policy_selection.py`

Implements expected free energy minimization for action selection:

```python
from geo_infer_act.core.policy_selection import PolicySelector

selector = PolicySelector(
    planning_horizon=20,
    discount_factor=0.95,
    exploration_temperature=1.0
)

# Generate policy space
policies = selector.generate_policies(
    current_beliefs=beliefs,
    goal_states=objectives,
    action_repertoire=available_actions
)

# Select optimal policy
optimal_policy = selector.select_policy(
    policies=policies,
    expected_free_energies=policy_values,
    selection_criterion='minimum_efe'
)
```

## Generative Models

### Generative Model Framework

**Location**: `core/generative_model.py`

Defines the structure for generative models of environmental dynamics:

```python
from geo_infer_act.core.generative_model import GenerativeModel

# Define generative model for spatial-temporal processes
model = GenerativeModel()

# Define state space (hidden variables)
model.define_states({
    'spatial_position': 'continuous_2d',
    'environmental_state': 'categorical',
    'agent_goals': 'multidimensional'
})

# Define observation model (likelihood)
model.define_observations({
    'remote_sensing': 'satellite_data',
    'sensor_networks': 'iot_measurements',
    'temporal_patterns': 'time_series'
})

# Define action model (transition dynamics)
model.define_actions({
    'navigation': 'movement_commands',
    'sampling': 'measurement_collection',
    'communication': 'information_sharing'
})
```

## Specialized Models

### Ecological Monitoring

**Location**: `models/ecological.py`

Active Inference agents for ecological systems:

```python
from geo_infer_act.models.ecological import EcologicalMonitor

monitor = EcologicalMonitor(
    ecosystem_type='forest',
    species_of_interest=['endangered_species'],
    environmental_factors=['temperature', 'precipitation', 'disturbance']
)

# Monitor ecological state
assessment = monitor.assess_ecosystem_state(sensor_data)
predictions = monitor.predict_ecological_changes(assessment)
```

### Urban Planning

**Location**: `models/urban.py`

Active Inference for urban development planning:

```python
from geo_infer_act.models.urban import UrbanPlanner

planner = UrbanPlanner(
    planning_area=city_bounds,
    planning_horizon=30,
    stakeholder_priorities=['sustainability', 'equity', 'efficiency']
)

# Generate urban development scenarios
scenarios = planner.generate_scenarios(current_state, future_drivers)
optimal_plan = planner.optimize_plan(scenarios, objectives, constraints)
```

### Climate Adaptation

**Location**: `models/climate.py`

Active Inference for climate change adaptation:

```python
from geo_infer_act.models.climate import ClimateAdaptationAgent

agent = ClimateAdaptationAgent(
    region=vulnerable_area,
    climate_hazards=['flooding', 'heat_waves'],
    adaptation_measures=['retreat', 'protect', 'transform']
)

# Assess climate vulnerabilities
vulnerabilities = agent.assess_vulnerabilities(hazard_data, exposure_data)
strategies = agent.develop_strategies(vulnerabilities, available_measures)
```

## Utility Functions

### Analysis Tools

**Location**: `utils/analysis.py`

Performance analysis and interpretability tools:

```python
from geo_infer_act.utils.analysis import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# Analyze agent performance
metrics = analyzer.analyze_performance(agent_trajectory, task_environment)
report = analyzer.generate_report(metrics, include_visualizations=True)
```

### Geospatial AI Utilities

**Location**: `utils/geospatial_ai.py`

Geospatial-specific AI utilities:

```python
from geo_infer_act.utils.geospatial_ai import GeospatialAI

geo_ai = GeospatialAI()

# Spatial reasoning
spatial_patterns = geo_ai.extract_spatial_patterns(geospatial_data)
relationships = geo_ai.analyze_spatial_relationships(patterns)
```

### Visualization Tools

**Location**: `utils/visualization.py`

Visualization of Active Inference processes:

```python
from geo_infer_act.utils.visualization import ActiveInferenceVisualizer

visualizer = ActiveInferenceVisualizer()

# Visualize belief updating
belief_plot = visualizer.plot_belief_evolution(belief_trajectory)

# Visualize free energy landscape
energy_plot = visualizer.plot_free_energy_landscape(beliefs, observations)
```

## API Interfaces

### REST API

**Location**: `api/endpoints.py`

RESTful API for Active Inference services:

```python
from geo_infer_act.api.endpoints import create_api

app = create_api()
app.run(host='0.0.0.0', port=8000)
```

Endpoints include:
- `POST /agents`: Create new Active Inference agent
- `GET /agents/{id}/beliefs`: Get agent beliefs
- `POST /agents/{id}/perceive`: Update agent with observations
- `GET /agents/{id}/actions`: Get agent action recommendations

### Client Library

**Location**: `api/client.py`

Python client for interacting with Active Inference services:

```python
from geo_infer_act.api.client import ActiveInferenceClient

client = ActiveInferenceClient(base_url='http://localhost:8000')

# Create and interact with remote agent
agent_id = client.create_agent(config=agent_configuration)
beliefs = client.get_beliefs(agent_id)
actions = client.request_actions(agent_id, observations)
```

## Development Guidelines

### Adding New Models

1. Create new model class in appropriate `models/` subdirectory
2. Extend base model classes from `models/base.py`
3. Implement required Active Inference components
4. Add comprehensive tests
5. Update documentation

### Testing

Run the complete test suite:
```bash
python -m pytest tests/
```

Run specific component tests:
```bash
python -m pytest tests/test_core.py::test_active_inference_agent
```

### Performance Optimization

- Use vectorized operations for batch processing
- Implement efficient variational inference algorithms
- Cache expensive computations when possible
- Profile code for bottlenecks

## Integration Points

The ACT module integrates with:

- **GEO-INFER-SPACE**: Spatial reasoning and coordinate systems
- **GEO-INFER-TIME**: Temporal dynamics and forecasting
- **GEO-INFER-DATA**: Data processing and management
- **GEO-INFER-AI**: Machine learning components
- **GEO-INFER-AGENT**: Agent lifecycle management
- **GEO-INFER-SIM**: Simulation environments

## Dependencies

- `numpy`: Numerical computations
- `scipy`: Scientific computing and optimization
- `jax`: Automatic differentiation (optional, for advanced VI)
- `matplotlib`: Visualization
- `networkx`: Graph algorithms
- `geopandas`: Geospatial data handling
