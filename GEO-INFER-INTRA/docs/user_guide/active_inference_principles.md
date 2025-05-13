# Active Inference Principles in GEO-INFER

This guide provides an overview of the core active inference principles used in the GEO-INFER framework and explains how they are applied to geospatial problems.

## What is Active Inference?

Active inference is a unified framework for understanding perception, learning, and decision-making based on the Free Energy Principle. It proposes that adaptive systems (from cells to societies) minimize the difference between their internal models and the external world through a combination of:

1. **Perception**: Updating internal models based on sensory observations
2. **Action**: Changing the environment to make it match predictions
3. **Learning**: Refining the internal model over time

In active inference, agents maintain probabilistic beliefs about the world and act to minimize surprise (or free energy) by either:
- Updating beliefs to match sensory inputs (perception)
- Taking actions that make sensory inputs match predictions (action)

## Core Mathematical Concepts

### Free Energy

The variational free energy is a measure of the difference between an agent's internal model and reality:

$$F = E_Q[\ln Q(s) - \ln P(o, s)]$$

Where:
- $Q(s)$ is the agent's beliefs about hidden states
- $P(o, s)$ is the generative model relating hidden states to observations
- $E_Q$ denotes expectation with respect to $Q$

### Expected Free Energy

Expected free energy guides action selection by balancing:

$$G(\pi) = \underbrace{D_{KL}[Q(s_\tau|\pi) || P(s_\tau)]}_{\text{Pragmatic value}} - \underbrace{E_{Q(o_\tau, s_\tau|\pi)}[\ln P(o_\tau|s_\tau)]}_{\text{Epistemic value}}$$

Where:
- $\pi$ is a policy (sequence of actions)
- The first term represents pragmatic value (goal-seeking)
- The second term represents epistemic value (information-seeking)

### Belief Updating

In active inference, beliefs are updated according to:

$$Q_{t+1}(s) \propto Q_t(s) \times P(o_t|s)$$

This Bayesian update combines prior beliefs with new observations.

## Geospatial Applications of Active Inference

### Spatial Belief Maps

In GEO-INFER, spatial belief maps represent probabilistic beliefs about variables distributed across space:

```python
from geo_infer_act import spatial_inference
import numpy as np

# Creating a spatial belief map for temperature
belief_map = spatial_inference.SpatialBeliefMap(
    variable="temperature",
    bbox=(-122.5, 37.7, -122.3, 37.9),
    resolution=9,  # H3 resolution
    prior_mean=20,
    prior_variance=4
)

# Updating with observations
belief_map.update([
    {"location": (37.7749, -122.4194), "value": 18.5},
    {"location": (37.7849, -122.4294), "value": 17.8}
])

# Visualizing the belief map
belief_map.visualize(
    show_uncertainty=True,
    cmap="coolwarm"
)
```

This creates a probabilistic map where:
- Areas near observations have lower uncertainty
- The mean at each location is influenced by nearby observations
- Spatial correlation is incorporated into the belief structure

### Adaptive Spatial Sampling

Active inference guides intelligent spatial sampling by maximizing information gain:

```python
from geo_infer_act import sampling
from geo_infer_space import visualization

# With an existing belief map
next_locations = sampling.optimal_sampling_locations(
    belief_map,
    n_locations=5,
    method="expected_information_gain"
)

# Visualize the recommended sampling locations
visualization.plot_sampling_strategy(
    belief_map,
    next_locations,
    title="Optimal Sampling Locations"
)
```

This approach:
- Prioritizes locations with high uncertainty
- Considers spatial correlation structure
- Balances exploration (high uncertainty) with exploitation (near interesting features)

### Environmental Monitoring

Active inference provides a framework for adaptive environmental monitoring:

```python
from geo_infer_act import monitoring
from geo_infer_time import forecasting

# Create a monitoring system
monitor = monitoring.AdaptiveMonitoringSystem(
    variables=["temperature", "pollution"],
    spatial_resolution=8,  # H3 resolution
    temporal_resolution="1D"  # Daily
)

# Update with new observations
monitor.update(new_observations)

# Get anomaly detection
anomalies = monitor.detect_anomalies(
    threshold=0.95,  # 95% confidence interval
    variables=["pollution"]
)

# Generate optimal monitoring schedule
schedule = monitor.generate_sampling_schedule(
    n_stations=10,
    time_horizon="7D",  # 7 days
    budget_constraint=100  # Cost constraint
)
```

This approach enables:
- Anomaly detection based on prediction errors
- Resource-efficient monitoring strategies
- Adaptive deployment of sensors

## Deep Dives: Geospatial Active Inference

### Example 1: Urban Temperature Prediction

```python
from geo_infer_act import generative_models
from geo_infer_space import features
import geopandas as gpd

# Load urban data
city = gpd.read_file("path/to/city.geojson")

# Extract spatial features
spatial_features = features.extract_urban_features(
    city,
    features=["building_density", "green_space", "elevation"]
)

# Create generative model
model = generative_models.SpatioTemporalGenerativeModel(
    spatial_resolution=9,
    temporal_resolution="1H",
    variables=["temperature"],
    features=["building_density", "green_space", "elevation"]
)

# Train model
model.fit(
    spatial_features=spatial_features,
    observations=temperature_observations
)

# Generate predictions
predictions = model.predict(
    horizon="24H",
    uncertainty=True
)

# Update with new observations
model.update(new_observations)
```

This model:
- Creates a generative model relating urban features to temperature
- Updates based on observations (perception)
- Predicts future states with uncertainty quantification
- Can guide interventions (e.g., where to plant trees to reduce heat)

### Example 2: Agent-Based Movement

```python
from geo_infer_agent import spatial_agent
from geo_infer_space import environment

# Create spatial environment
env = environment.SpatialEnvironment(
    bounds=city_bounds,
    obstacles=buildings,
    features={"elevation": dem}
)

# Create active inference agent
agent = spatial_agent.ActiveInferenceAgent(
    environment=env,
    initial_position=start_location,
    goal=destination,
    precision=5.0
)

# Run simulation
trajectories = agent.simulate(
    steps=100,
    planning_horizon=10
)

# Visualize agent behavior
spatial_agent.visualize_trajectory(
    environment=env,
    trajectories=trajectories
)
```

The agent:
- Maintains beliefs about the environment
- Selects actions that minimize expected free energy
- Balances goal-directed behavior with exploration
- Adapts to unexpected obstacles

### Example 3: Risk Assessment

```python
from geo_infer_risk import assessment
from geo_infer_act import decision_making

# Create risk assessment model
risk_model = assessment.ActiveInferenceRiskModel(
    hazard_type="flood",
    spatial_resolution=8,
    temporal_resolution="1D"
)

# Train with historical data
risk_model.fit(
    historical_hazards=flood_history,
    vulnerability_data=vulnerability_map,
    asset_data=buildings
)

# Generate risk predictions
risk_predictions = risk_model.predict(
    weather_forecast=forecast_data,
    time_horizon="7D"
)

# Determine optimal interventions
interventions = decision_making.optimal_interventions(
    risk_model=risk_model,
    intervention_options=available_interventions,
    budget_constraint=1000000,
    objective="minimize_expected_damage"
)
```

This approach:
- Quantifies risk as a function of hazard, vulnerability, and exposure
- Updates beliefs based on new data
- Guides intervention decisions to minimize expected loss
- Balances costs of intervention against potential benefits

## Key Principles in Practice

### 1. Uncertainty Representation

In GEO-INFER, all predictions include uncertainty:

```python
# Probability distribution over values
temperature_belief = model.get_belief(location=(37.7749, -122.4194))

# Mean and variance
mean = temperature_belief.mean
variance = temperature_belief.variance

# Credible intervals
intervals = temperature_belief.credible_intervals(alpha=0.95)
lower, upper = intervals["lower"], intervals["upper"]

# Visualizing uncertainty
maps.plot_prediction_with_uncertainty(
    prediction_map,
    uncertainty_metric="variance",
    cmap="viridis"
)
```

### 2. Information-Seeking Behavior

Active inference naturally drives exploration:

```python
# Calculate expected information gain
info_gain = model.expected_information_gain(
    potential_locations=candidate_locations
)

# Select next sampling location
next_location = candidate_locations[np.argmax(info_gain)]
```

### 3. Precision Weighting

Active inference weights evidence by its reliability:

```python
# Set precision for different data sources
model.set_precision(
    variable="temperature",
    source="satellite",
    precision=1.0  # Lower precision (higher uncertainty)
)

model.set_precision(
    variable="temperature",
    source="ground_station",
    precision=5.0  # Higher precision (lower uncertainty)
)
```

### 4. Hierarchical Models

GEO-INFER supports multi-scale hierarchical models:

```python
# Create hierarchical model
model = hierarchical.SpatioTemporalHierarchicalModel(
    resolutions=[6, 9, 12],  # H3 resolutions
    temporal_scales=["1D", "1H", "5min"]
)

# Information flows both ways:
# - Top-down (constraints from larger scales)
# - Bottom-up (evidence from smaller scales)
```

## Further Reading

- [Mathematical Foundations](../technical/active_inference_math.md)
- [Implementation Details](../developer_guide/implementing_active_inference.md)
- [Practical Examples](../examples/active_inference/index.md)
- [Research Papers](../references/active_inference_bibliography.md) 