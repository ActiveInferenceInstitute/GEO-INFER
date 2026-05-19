# Active Inference Guide for GEO-INFER

## Introduction

Active Inference is a mathematical framework, rooted in the Free Energy Principle,
that unifies perception, learning, and decision-making under a single objective:
minimizing variational free energy. Biological organisms, from single cells to
entire ecosystems, can be described as systems that maintain their structural
integrity by predicting their sensory inputs and acting to fulfill those predictions.

GEO-INFER applies Active Inference to geospatial systems. Rather than treating
spatial analysis as static computation over fixed datasets, GEO-INFER models
geographic entities --- habitats, urban zones, watersheds, agricultural fields ---
as adaptive agents that maintain beliefs about their environment, update those
beliefs when new observations arrive, and select actions that minimize expected
surprise. This produces systems that actively seek information, resolve uncertainty,
and adapt to changing conditions.

The framework is implemented primarily in the `GEO-INFER-ACT` module, with
supporting functionality distributed across `GEO-INFER-BAYES` (probabilistic
inference), `GEO-INFER-COG` (cognitive modeling), `GEO-INFER-AGENT` (multi-agent
systems), and `GEO-INFER-SPM` (statistical parametric mapping).

## The Free Energy Principle

### Mathematical Foundation

The Free Energy Principle states that any self-organizing system at equilibrium
with its environment must minimize its variational free energy. For a system with
observations `o`, hidden states `s`, and approximate posterior `q(s)`:

```
F = E_q[log q(s) - log p(o, s)]
```

This decomposes into two equivalent forms:

**Energy minus entropy:**

```
F = E_q[-log p(o, s)] - H[q(s)]
```

Where `H[q(s)]` is the entropy of the approximate posterior.

**Complexity minus accuracy:**

```
F = D_KL[q(s) || p(s)] - E_q[log p(o | s)]
```

Where:
- `D_KL[q(s) || p(s)]` is the complexity (divergence of posterior from prior)
- `E_q[log p(o | s)]` is the accuracy (expected log-likelihood)

### Perceptual Inference

Perceptual inference updates beliefs about hidden states to explain incoming
observations. The agent holds the world fixed and adjusts its internal model:

```
q*(s) = argmin_q F[q, o]
```

In geospatial terms: given satellite imagery of a forest, the system updates its
beliefs about tree density, canopy height, and species composition to best explain
the pixel values it observes.

### Active Inference

Active inference extends perception to action. The agent selects actions that
minimize *expected* free energy over future time steps:

```
G(pi) = E_q(o,s|pi)[ log q(s|pi) - log p(o, s) ]
```

This expected free energy `G` decomposes into:
- **Pragmatic value**: achieving preferred outcomes (goal-directed behavior)
- **Epistemic value**: reducing uncertainty about hidden states (exploration)

The agent naturally balances exploitation and exploration without requiring
separate mechanisms for each.

## Core Concepts

### Generative Model

A generative model specifies how hidden states produce observations. In GEO-INFER,
the generative model for a geospatial agent consists of:

| Component | Symbol | Description | GEO-INFER Implementation |
|-----------|--------|-------------|--------------------------|
| Prior beliefs | `D` | Initial distribution over states | `GenerativeModel.state_prior` |
| Likelihood | `A` | Mapping from states to observations | `GenerativeModel.observation_model` |
| Transitions | `B` | State dynamics under actions | `GenerativeModel.transition_model` |
| Preferences | `C` | Desired observations | `GenerativeModel.preferences` |
| Policies | `E` | Prior over action sequences | `PolicySelector.policy_prior` |

```python
from geo_infer_act.core.generative_model import GenerativeModel
import numpy as np

# 4 hidden states: forest, agriculture, urban, water
num_states = 4
num_observations = 6  # spectral band categories

# Define a generative model for land-use classification
model = GenerativeModel(
    "categorical",
    {"state_dim": num_states, "obs_dim": num_observations},
)

# Likelihood: how each land type produces spectral observations
A = np.array([
    [0.7, 0.1, 0.05, 0.05],  # high green reflectance
    [0.1, 0.5, 0.1, 0.05],   # moderate green reflectance
    [0.05, 0.2, 0.6, 0.05],  # high built-up index
    [0.05, 0.1, 0.1, 0.7],   # high water index
    [0.05, 0.05, 0.1, 0.1],  # thermal signature
    [0.05, 0.05, 0.05, 0.05] # noise
])
model.observation_model = A

# Prior: uniform belief over land types before observation
D = np.array([0.25, 0.25, 0.25, 0.25])
model.beliefs["states"] = D
```

### Markov Blanket

A Markov blanket defines the boundary between a system and its environment. It
consists of sensory states (receiving information) and active states (influencing
the environment). Internal states are conditionally independent of external states
given the blanket.

In geospatial applications, the Markov blanket maps to:
- **Sensory states**: Remote sensing data, sensor readings, survey observations
- **Active states**: Land management decisions, urban planning interventions,
  conservation actions
- **Internal states**: Model parameters, beliefs about hidden spatial processes
- **External states**: The actual state of the environment (true soil moisture,
  real population density)

### Variational Bayes

Exact Bayesian inference is intractable for most real-world models. Variational
Bayes approximates the true posterior `p(s|o)` with a tractable distribution
`q(s)` by minimizing the KL divergence between them. Since minimizing
`D_KL[q(s) || p(s|o)]` requires knowing the true posterior, we instead minimize
the free energy `F`, which provides an upper bound on surprise:

```
F = D_KL[q(s) || p(s|o)] + (-log p(o))
```

Since `D_KL >= 0`, minimizing `F` simultaneously tightens the bound on the log
evidence and brings `q(s)` closer to the true posterior.

### Precision-Weighting

Precision is the inverse variance of a probability distribution. In Active
Inference, precision weights the relative influence of priors versus sensory
evidence:

- **High sensory precision**: the agent trusts its observations (data-driven)
- **High prior precision**: the agent trusts its model (model-driven)
- **Balanced precision**: the agent weighs both sources appropriately

In geospatial applications, precision maps to data quality. A high-resolution
satellite image has high sensory precision. A well-validated climate model has
high prior precision. Cloud-covered imagery has low sensory precision, causing the
agent to rely more on its prior beliefs.

```python
from geo_infer_act.core.free_energy import FreeEnergyCalculator

calculator = FreeEnergyCalculator()

beliefs = np.array([0.3, 0.3, 0.2, 0.2])
observations = np.array([0.8, 0.1, 0.05, 0.05])

# Low precision: agent barely updates from observation
low_precision_fe = calculator.compute_categorical_free_energy(
    beliefs=beliefs,
    observations=observations * 0.5 + 0.5 / len(observations),  # flattened
)

# High precision: agent updates strongly toward observation
high_precision_fe = calculator.compute_categorical_free_energy(
    beliefs=beliefs,
    observations=observations,
)
```

## Perception-Action Loops in Geospatial Context

### Habitat Tracking

Consider tracking wildlife habitat quality across a landscape. The Active
Inference loop operates as follows:

1. **Predict**: The agent predicts expected NDVI values, soil moisture, and
   canopy cover based on its current beliefs about habitat state.
2. **Observe**: New satellite imagery arrives, providing actual NDVI values.
3. **Update**: The agent computes prediction error (difference between predicted
   and observed NDVI) and updates beliefs about habitat quality.
4. **Act**: Based on updated beliefs and expected free energy, the agent
   recommends where to deploy field surveys (epistemic action) or where to
   prioritize conservation efforts (pragmatic action).
5. **Repeat**: The cycle continues with each new observation.

### Urban Mobility

For urban mobility prediction:

1. **Predict**: The agent predicts traffic flow patterns based on beliefs about
   road network state, time of day, and event schedules.
2. **Observe**: IoT sensors and GPS traces provide actual flow measurements.
3. **Update**: Prediction errors drive belief updates about congestion,
   incidents, and demand patterns.
4. **Act**: The agent recommends traffic signal adjustments, route suggestions,
   or transit schedule changes that minimize expected free energy (reduce
   uncertainty about future states while achieving desired flow patterns).

## Belief Updating with Spatial Priors

Geospatial belief updating extends standard Active Inference by incorporating
spatial structure into the prior. Nearby locations are assumed to have correlated
hidden states, encoded through spatial kernels or adjacency matrices on H3 grids.

```python
import numpy as np
import h3

def create_spatial_prior(center_lat: float, center_lng: float,
                         resolution: int = 8, k_rings: int = 3,
                         decay_rate: float = 1.0) -> dict:
    """
    Create a spatially-structured prior over H3 cells.

    The prior probability decreases exponentially with distance from
    the center cell, encoding the assumption that nearby locations
    share similar hidden states.

    Args:
        center_lat: Latitude of the center point.
        center_lng: Longitude of the center point.
        resolution: H3 resolution (0-15).
        k_rings: Number of rings around the center cell.
        decay_rate: Controls how rapidly the prior decays with distance.

    Returns:
        Dictionary mapping H3 cell IDs to prior probabilities.
    """
    center_cell = h3.latlng_to_cell(center_lat, center_lng, resolution)
    cells = h3.grid_disk(center_cell, k_rings)

    center_latlng = h3.cell_to_latlng(center_cell)
    prior = {}

    for cell in cells:
        cell_latlng = h3.cell_to_latlng(cell)
        # Approximate distance using Euclidean on lat/lng (valid for small areas)
        dlat = cell_latlng[0] - center_latlng[0]
        dlng = cell_latlng[1] - center_latlng[1]
        dist = np.sqrt(dlat**2 + dlng**2)
        prior[cell] = np.exp(-decay_rate * dist)

    # Normalize to form a valid distribution
    total = sum(prior.values())
    for cell in prior:
        prior[cell] /= total

    return prior


# Create a spatial prior centered on a forest region
prior = create_spatial_prior(
    center_lat=47.6062,
    center_lng=-122.3321,
    resolution=8,
    k_rings=3,
    decay_rate=50.0
)
print(f"Prior covers {len(prior)} H3 cells")
print(f"Center cell probability: {max(prior.values()):.4f}")
print(f"Edge cell probability: {min(prior.values()):.6f}")
```

Belief updating then combines this spatial prior with incoming observations:

```python
def update_spatial_beliefs(prior: dict, observations: dict,
                           likelihood_model: dict,
                           precision: float = 1.0) -> dict:
    """
    Update spatial beliefs using Bayesian inference with precision weighting.

    Args:
        prior: Dictionary mapping H3 cell IDs to prior probabilities.
        observations: Dictionary mapping H3 cell IDs to observed values.
        likelihood_model: Dictionary mapping H3 cell IDs to likelihood values.
        precision: Sensory precision (inverse variance). Higher values weight
                   observations more heavily.

    Returns:
        Dictionary mapping H3 cell IDs to posterior probabilities.
    """
    posterior = {}

    for cell, prior_prob in prior.items():
        if cell in observations and cell in likelihood_model:
            # Precision-weighted likelihood
            log_likelihood = precision * np.log(
                likelihood_model[cell] + 1e-16
            )
            log_prior = np.log(prior_prob + 1e-16)
            posterior[cell] = np.exp(log_prior + log_likelihood)
        else:
            # No observation: posterior equals prior
            posterior[cell] = prior_prob

    # Normalize
    total = sum(posterior.values())
    if total > 0:
        for cell in posterior:
            posterior[cell] /= total

    return posterior
```

## GEO-INFER-ACT Integration

The `GEO-INFER-ACT` module provides the core Active Inference implementation.
For production H3 or spatial runs, prefer the package runner contract:
`geo-infer-act-run --scenario h3` or `--scenario spatial`. Those scenarios use
real H3 v4 cells, normalized beliefs, finite FE/EFE diagnostics, GIS-ready CSV
and GeoJSON outputs, manifest-linked visualizations, embedded figure metadata,
and per-figure metadata plus plotted-data sidecars. The canonical output and
validation contract is
[`GEO-INFER-ACT/docs/geospatial_applications.md`](../../GEO-INFER-ACT/docs/geospatial_applications.md).

### Creating an Active Inference Agent

```python
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.core.policy_selection import PolicySelector
import numpy as np

# Configure state space: 5 habitat quality levels
num_states = 5
num_obs = 4  # NDVI categories: low, medium, high, very_high

# Step 1: Define the generative model
model = GenerativeModel(
    "categorical",
    {"state_dim": num_states, "obs_dim": num_obs},
)

# Likelihood matrix: P(observation | state)
A = np.zeros((num_obs, num_states))
A[0, :] = [0.7, 0.2, 0.05, 0.03, 0.02]  # low NDVI
A[1, :] = [0.2, 0.5, 0.2, 0.07, 0.03]    # medium NDVI
A[2, :] = [0.07, 0.2, 0.5, 0.4, 0.2]     # high NDVI
A[3, :] = [0.03, 0.1, 0.25, 0.5, 0.75]   # very high NDVI
model.observation_model = A

# Transition matrix: P(s' | s, action=no_intervention)
B = np.eye(num_states) * 0.7
for i in range(num_states - 1):
    B[i + 1, i] = 0.2   # natural improvement
    B[i, i + 1] = 0.1   # natural degradation
model.transition_model = B

# Prior beliefs: start with moderate habitat quality
D = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
model.beliefs["states"] = D

# Step 2: Create the Active Inference agent
agent = ActiveInferenceModel(model_type="categorical")
agent.set_generative_model(model)

# Step 3: Present observations and update beliefs
observation = np.array([0.05, 0.15, 0.5, 0.3])  # high NDVI observed
updated_beliefs = agent.perceive(observation)
print(f"Updated beliefs about habitat quality: {updated_beliefs}")
```

### Worked Example 1: Wildlife Habitat Tracking

This example demonstrates tracking habitat quality across a landscape using
free energy minimization. The agent monitors NDVI values and updates its beliefs
about habitat suitability for a target species.

```python
import numpy as np
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator

# Define habitat quality states
STATES = ["degraded", "poor", "moderate", "good", "pristine"]
NUM_STATES = len(STATES)

# Observation categories from remote sensing
OBS_CATEGORIES = ["bare_soil", "sparse_vegetation", "moderate_canopy", "dense_canopy"]
NUM_OBS = len(OBS_CATEGORIES)

# Build the generative model
habitat_model = GenerativeModel(
    "categorical",
    {"state_dim": NUM_STATES, "obs_dim": NUM_OBS},
)

# Likelihood: how habitat quality produces remote sensing signatures
A = np.array([
    [0.75, 0.30, 0.10, 0.03, 0.01],  # bare soil
    [0.15, 0.40, 0.25, 0.10, 0.04],  # sparse vegetation
    [0.07, 0.20, 0.40, 0.37, 0.20],  # moderate canopy
    [0.03, 0.10, 0.25, 0.50, 0.75],  # dense canopy
])
habitat_model.observation_model = A

# Transition dynamics: seasonal improvement expected (spring)
B_spring = np.array([
    [0.60, 0.05, 0.00, 0.00, 0.00],
    [0.30, 0.55, 0.05, 0.00, 0.00],
    [0.08, 0.30, 0.60, 0.10, 0.02],
    [0.02, 0.08, 0.25, 0.60, 0.18],
    [0.00, 0.02, 0.10, 0.30, 0.80],
])
habitat_model.transition_model = B_spring

# Prior: start from uninformed position
D = np.ones(NUM_STATES) / NUM_STATES
habitat_model.beliefs["states"] = D

# Create the agent
agent = ActiveInferenceModel(model_type="categorical")
agent.set_generative_model(habitat_model)

# Simulate a sequence of observations over 6 time steps
observation_sequence = [
    np.array([0.10, 0.20, 0.45, 0.25]),  # moderate canopy signal
    np.array([0.05, 0.15, 0.35, 0.45]),  # improving toward dense
    np.array([0.03, 0.10, 0.30, 0.57]),  # more dense canopy
    np.array([0.02, 0.08, 0.25, 0.65]),  # continuing improvement
    np.array([0.15, 0.35, 0.30, 0.20]),  # sudden degradation (disturbance)
    np.array([0.10, 0.25, 0.40, 0.25]),  # partial recovery
]

calculator = FreeEnergyCalculator()

print("Habitat Tracking Over 6 Time Steps")
print("=" * 60)

beliefs = D.copy()
for t, obs in enumerate(observation_sequence):
    # Update beliefs via perception
    beliefs = agent.perceive(obs)

    # Compute free energy to measure model fit
    fe = calculator.compute_categorical_free_energy(
        beliefs=beliefs,
        observations=obs,
    )

    most_likely = STATES[np.argmax(beliefs)]
    confidence = np.max(beliefs)
    print(f"t={t}: Most likely state = {most_likely} "
          f"(confidence={confidence:.3f}), Free energy = {fe:.4f}")
```

### Worked Example 2: Urban Mobility Prediction

This example uses belief updating to predict traffic patterns across an
H3-indexed urban grid.

```python
import numpy as np
import h3

# Define the urban grid using H3
city_center_lat, city_center_lng = 37.7749, -122.4194  # San Francisco
resolution = 9  # ~0.1 km^2 per cell

center_cell = h3.latlng_to_cell(city_center_lat, city_center_lng, resolution)
neighborhood = list(h3.grid_disk(center_cell, 2))  # 2-ring neighborhood
num_cells = len(neighborhood)

# Traffic states per cell: free_flow, moderate, congested, gridlock
NUM_TRAFFIC_STATES = 4
TRAFFIC_LABELS = ["free_flow", "moderate", "congested", "gridlock"]

# Initialize beliefs: assume free flow everywhere at midnight
beliefs = np.zeros((num_cells, NUM_TRAFFIC_STATES))
beliefs[:, 0] = 0.85  # mostly free flow
beliefs[:, 1] = 0.10
beliefs[:, 2] = 0.04
beliefs[:, 3] = 0.01

# Transition model for morning rush hour (7-9 AM)
# Traffic tends to worsen (shift toward congested/gridlock)
rush_hour_transition = np.array([
    [0.40, 0.10, 0.02, 0.01],  # free_flow -> ...
    [0.40, 0.40, 0.08, 0.04],  # moderate -> ...
    [0.15, 0.35, 0.50, 0.25],  # congested -> ...
    [0.05, 0.15, 0.40, 0.70],  # gridlock -> ...
])

# Simulate morning rush: apply transition to all cells
predicted_beliefs = np.zeros_like(beliefs)
for i in range(num_cells):
    predicted_beliefs[i] = rush_hour_transition.T @ beliefs[i]

# Simulated sensor observations at 8 AM (some cells have sensors)
sensor_cells = [0, 3, 7]  # indices of cells with traffic sensors
sensor_readings = {
    0: np.array([0.1, 0.3, 0.4, 0.2]),   # congested
    3: np.array([0.5, 0.3, 0.15, 0.05]),  # moderate
    7: np.array([0.05, 0.15, 0.3, 0.5]),  # gridlock
}

# Bayesian update: combine predictions with sensor data
SENSOR_PRECISION = 2.0

for idx, sensor_obs in sensor_readings.items():
    prior = predicted_beliefs[idx]
    # Precision-weighted update
    log_posterior = np.log(prior + 1e-16) + SENSOR_PRECISION * np.log(sensor_obs + 1e-16)
    posterior = np.exp(log_posterior - np.max(log_posterior))
    posterior /= posterior.sum()
    predicted_beliefs[idx] = posterior

# Propagate information to adjacent cells (spatial smoothing)
cell_to_idx = {cell: i for i, cell in enumerate(neighborhood)}

for i, cell in enumerate(neighborhood):
    neighbors = [n for n in h3.grid_disk(cell, 1) if n in cell_to_idx and n != cell]
    if neighbors:
        neighbor_beliefs = np.mean(
            [predicted_beliefs[cell_to_idx[n]] for n in neighbors], axis=0
        )
        # Light spatial smoothing (80% local, 20% neighbor average)
        predicted_beliefs[i] = 0.8 * predicted_beliefs[i] + 0.2 * neighbor_beliefs
        predicted_beliefs[i] /= predicted_beliefs[i].sum()

# Report results
print("Urban Mobility Prediction - 8 AM Rush Hour")
print("=" * 55)
for i, cell in enumerate(neighborhood[:5]):
    state = TRAFFIC_LABELS[np.argmax(predicted_beliefs[i])]
    conf = np.max(predicted_beliefs[i])
    sensor_flag = " [SENSOR]" if i in sensor_cells else ""
    print(f"Cell {cell[:12]}...: {state} (confidence={conf:.3f}){sensor_flag}")
```

## Module Integration Table

| Module | Role in Active Inference | Key Classes/Functions |
|--------|--------------------------|----------------------|
| **GEO-INFER-ACT** | Core Active Inference engine | `ActiveInferenceModel`, `GenerativeModel`, `FreeEnergyCalculator`, `PolicySelector`, `BayesianBeliefUpdate` |
| **GEO-INFER-BAYES** | Probabilistic inference backends | `GaussianProcess`, `MCMC`, `VariationalInference`, `ModelComparison` |
| **GEO-INFER-COG** | Cognitive modeling, attention, perception | Attention mechanisms, cognitive maps, perceptual hierarchies |
| **GEO-INFER-AGENT** | Multi-agent Active Inference systems | Agent coordination, communication, collective inference |
| **GEO-INFER-SPM** | Statistical parametric mapping for spatial inference | Spatial GLMs, random field theory, voxel-based analysis |
| **GEO-INFER-MATH** | Mathematical foundations | Linear algebra utilities, optimization, spatial statistics |
| **GEO-INFER-SPACE** | Spatial indexing and operations | H3 grid operations, spatial queries, geometry processing |
| **GEO-INFER-TIME** | Temporal dynamics | Time series analysis, temporal belief propagation |
| **GEO-INFER-SIM** | Simulation environments | Agent-based simulation, environment models |

### Integration Pattern

```
Observations (DATA/IOT) --> Perception (ACT + BAYES)
                               |
                          Belief Update
                               |
                       Policy Selection (ACT)
                               |
                          Action (AGENT)
                               |
                     Environment Change (SIM)
                               |
                   New Observations (cycle repeats)
```

## Key Mathematical Relationships

### Free Energy and Surprise

```
F >= -log p(o)   [free energy bounds surprise]
```

When `q(s) = p(s|o)`, free energy equals surprise. In practice, `q(s)` is an
approximation, so free energy is always greater than or equal to surprise.

### Expected Free Energy Decomposition

```
G(pi) = -E_q(o|pi)[D_KL[q(s|o,pi) || q(s|pi)]]  +  E_q(o|pi)[log q(o|pi) - log p(o)]
         |___________________________________|        |_________________________________|
                  Epistemic value                            Pragmatic value
                  (information gain)                         (goal achievement)
```

### Policy Selection via Softmax

```
P(pi) = sigma(-gamma * G(pi))
```

Where `gamma` is the precision over policies (inverse temperature) and `sigma` is
the softmax function.

## References and Further Reading

### Primary Sources

1. Friston, K. J. (2010). The free-energy principle: a unified brain theory?
   *Nature Reviews Neuroscience*, 11(2), 127-138.

2. Friston, K. J., FitzGerald, T., Rigoli, F., Schwartenbeck, P., & Pezzulo, G.
   (2017). Active inference: A process theory. *Neural Computation*, 29(1), 1-49.

3. Parr, T., & Friston, K. J. (2019). Generalised free energy and active
   inference. *Biological Cybernetics*, 113(5-6), 495-513.

4. Da Costa, L., Parr, T., Sajid, N., Vesber, S., Ryan, V., & Friston, K.
   (2020). Active inference on discrete state-spaces: A synthesis. *Journal of
   Mathematical Psychology*, 99, 102447.

### Tutorials and Overviews

5. Sajid, N., Ball, P. J., Parr, T., & Friston, K. J. (2021). Active inference:
   Demystified and compared. *Neural Computation*, 33(3), 674-712.

6. Smith, R., Friston, K. J., & Whyte, C. J. (2022). A step-by-step tutorial on
   active inference and its application to empirical data. *Journal of
   Mathematical Psychology*, 107, 102632.

### Software

7. `pymdp` - Python package for active inference on discrete state spaces.
   https://github.com/infer-actively/pymdp

8. `SPM` - Statistical Parametric Mapping software suite.
   https://www.fil.ion.ucl.ac.uk/spm/

### GEO-INFER Module Documentation

- [GEO-INFER-ACT README](../../GEO-INFER-ACT/README.md)
- [GEO-INFER-BAYES README](../../GEO-INFER-BAYES/README.md)
- [GEO-INFER-COG README](../../GEO-INFER-COG/README.md)
- [GEO-INFER-AGENT README](../../GEO-INFER-AGENT/README.md)
- [GEO-INFER-SPM README](../../GEO-INFER-SPM/README.md)
- [Bayesian Inference Guide](bayesian_inference_guide.md)
- [Terminology Glossary](terminology.md)
