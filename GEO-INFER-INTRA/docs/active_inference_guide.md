# GEO-INFER Active Inference Implementation Guide

This guide provides standards and best practices for implementing active inference principles across the GEO-INFER framework.

## Active Inference Overview

Active inference is a framework based on the free energy principle that provides a unified account of perception, learning, and decision-making. In GEO-INFER, we apply these principles to geospatial systems to model adaptive behavior across scales, from individuals to ecosystems.

### Key Concepts

- **Free Energy Principle**: Systems resist disorder by minimizing surprise (free energy)
- **Generative Models**: Internal models that predict sensory inputs
- **Belief Updating**: Updating internal models based on new evidence
- **Policy Selection**: Selecting actions that minimize expected free energy
- **Precision Weighting**: Weighting predictions and observations by their reliability

## Implementation Standards

### Mathematical Formalism

All active inference implementations should adhere to consistent mathematical notation:

| Symbol | Meaning | Implementation |
|--------|---------|----------------|
| $o$ | Observations | `observations` |
| $s$ | Hidden states | `states` |
| $\pi$ | Policies (action sequences) | `policies` |
| $a$ | Actions | `actions` |
| $P(o \mid s)$ | Likelihood (observation model) | `likelihood` or `observation_model` |
| $P(s)$ | Prior over states | `state_prior` |
| $P(s' \mid s, a)$ | Transition model | `transition_model` |
| $P(\pi \mid s)$ | Prior over policies | `policy_prior` |
| $Q(s)$ | Posterior beliefs about states | `state_beliefs` |
| $Q(\pi)$ | Posterior beliefs about policies | `policy_beliefs` |
| $\mathcal{F}$ | Variational free energy | `free_energy` |
| $\mathcal{G}$ | Expected free energy | `expected_free_energy` |
| $\gamma$ | Precision | `precision` |

### Generative Model Structure

Each generative model implementation should include:

1. **Prior Distribution**
   ```python
   def initialize_priors(self):
       """Initialize priors over states.
       
       Returns:
           Prior probability distribution over states
       """
       # Implementation
   ```

2. **Likelihood/Observation Model**
   ```python
   def observation_model(self, state):
       """Define mapping from hidden states to observations.
       
       Args:
           state: Current state
           
       Returns:
           Likelihood distribution P(o|s)
       """
       # Implementation
   ```

3. **Transition Model**
   ```python
   def transition_model(self, state, action):
       """Define state transitions given actions.
       
       Args:
           state: Current state
           action: Selected action
           
       Returns:
           Next state distribution P(s'|s,a)
       """
       # Implementation
   ```

4. **Preference Model**
   ```python
   def preference_model(self, observation):
       """Define agent preferences over observations.
       
       Args:
           observation: Potential observation
           
       Returns:
           Preference value (log probability)
       """
       # Implementation
   ```

### Inference Algorithms

Standard inference algorithms include:

1. **Variational Inference**
   ```python
   def variational_inference(self, observation):
       """Update beliefs using variational inference.
       
       Args:
           observation: Current observation
           
       Returns:
           Updated state beliefs Q(s)
       """
       # Implementation
   ```

2. **Message Passing**
   ```python
   def belief_propagation(self, observation):
       """Update beliefs using message passing.
       
       Args:
           observation: Current observation
           
       Returns:
           Updated state beliefs Q(s)
       """
       # Implementation
   ```

### Policy Selection

Standard methods for policy selection:

1. **Expected Free Energy Minimization**
   ```python
   def compute_expected_free_energy(self, policy):
       """Compute expected free energy for a policy.
       
       Args:
           policy: Sequence of actions
           
       Returns:
           Expected free energy value
       """
       # Implementation including:
       # - Epistemic value (information gain)
       # - Pragmatic value (goal achievement)
   ```

2. **Policy Selection**
   ```python
   def select_policy(self):
       """Select policy based on expected free energy.
       
       Returns:
           Selected policy (action sequence)
       """
       # Implementation
   ```

## Geospatial Active Inference

### Spatial State Representation

Guidelines for representing spatial states:

1. **Discrete State Spaces**
   - Use H3 hexagons for discrete spatial representation
   - Document resolution choice and rationale
   - Include adjacency relationships in transition models

2. **Continuous State Spaces**
   - Use Gaussian processes for continuous spatial fields
   - Document kernel choices and hyperparameters
   - Specify coordinate system and spatial bounds

Example:
```python
import h3
import numpy as np

class SpatialGenerativeModel:
    def __init__(self, resolution=8):
        """Initialize spatial generative model.
        
        Args:
            resolution: H3 resolution for spatial discretization
        """
        self.resolution = resolution
        self.states = {}  # Dictionary mapping H3 indices to state values
        self.adjacency = {}  # Dictionary mapping H3 indices to neighbors
        
    def initialize_spatial_priors(self, center_lat, center_lon, radius_km):
        """Initialize spatial priors centered at a location.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers
            
        Returns:
            Dictionary of H3 indices with prior probabilities
        """
        # Get hexagons within radius
        center_hex = h3.geo_to_h3(center_lat, center_lon, self.resolution)
        hexagons = h3.k_ring(center_hex, int(radius_km / h3.edge_length(self.resolution)))
        
        # Initialize priors with distance-based falloff
        priors = {}
        for hex_id in hexagons:
            hex_center = h3.h3_to_geo(hex_id)
            distance = self._haversine(center_lat, center_lon, hex_center[0], hex_center[1])
            priors[hex_id] = np.exp(-distance / radius_km)
            
        # Normalize
        total = sum(priors.values())
        for hex_id in priors:
            priors[hex_id] /= total
            
        return priors
```

### Temporal Dynamics

Guidelines for incorporating temporal dynamics:

1. **Temporal Resolution**
   - Match temporal resolution to process dynamics
   - Document time steps and units
   - Consider multiple timescales for hierarchical models

2. **Spatiotemporal Transitions**
   - Model both spatial and temporal dependencies
   - Consider anisotropic processes (e.g., directional flows)
   - Include seasonality where appropriate

Example:
```python
def spatiotemporal_transition(self, current_states, action, time_step):
    """Model spatiotemporal transitions.
    
    Args:
        current_states: Dictionary of current states by location
        action: Selected action
        time_step: Size of time step in appropriate units
        
    Returns:
        Dictionary of next states by location
    """
    # Implementation
```

### Multi-Scale Models

Guidelines for multi-scale active inference:

1. **Hierarchical Models**
   - Nest models at different spatial/temporal scales
   - Ensure consistent information flow between scales
   - Document scale boundaries and interfaces

2. **Message Passing Between Scales**
   - Downward messages (priors from higher to lower scales)
   - Upward messages (posteriors from lower to higher scales)
   - Lateral messages (between entities at the same scale)

Example hierarchical structure:
```python
class HierarchicalSpatialModel:
    def __init__(self):
        """Initialize hierarchical spatial model."""
        self.macro_model = SpatialGenerativeModel(resolution=6)  # Regional
        self.meso_model = SpatialGenerativeModel(resolution=9)   # Local
        self.micro_model = SpatialGenerativeModel(resolution=12) # Building
        
    def update_beliefs_hierarchical(self, observations):
        """Update beliefs across hierarchical levels.
        
        Args:
            observations: Dictionary of observations by scale and location
            
        Returns:
            Updated beliefs at all scales
        """
        # Update micro level with observations
        micro_posteriors = self.micro_model.update_beliefs(observations['micro'])
        
        # Aggregate micro posteriors to meso level
        aggregated_micro = self._aggregate_beliefs(micro_posteriors, 
                                                  from_resolution=12, 
                                                  to_resolution=9)
        
        # Update meso level with aggregated micro posteriors
        meso_posteriors = self.meso_model.update_beliefs(aggregated_micro)
        
        # Aggregate meso posteriors to macro level
        aggregated_meso = self._aggregate_beliefs(meso_posteriors,
                                                 from_resolution=9,
                                                 to_resolution=6)
        
        # Update macro level
        macro_posteriors = self.macro_model.update_beliefs(aggregated_meso)
        
        # Top-down predictions (priors for lower levels)
        meso_priors = self._disaggregate_beliefs(macro_posteriors,
                                               from_resolution=6,
                                               to_resolution=9)
        micro_priors = self._disaggregate_beliefs(meso_posteriors,
                                                from_resolution=9,
                                                to_resolution=12)
        
        # Incorporate top-down priors
        self.meso_model.update_priors(meso_priors)
        self.micro_model.update_priors(micro_priors)
        
        return {
            'micro': micro_posteriors,
            'meso': meso_posteriors,
            'macro': macro_posteriors
        }
```

## Implementation Examples

### Simple Spatial Agent

```python
import numpy as np
from scipy.special import softmax

class SpatialActiveInferenceAgent:
    def __init__(self, grid_size=(10, 10)):
        """Initialize spatial active inference agent.
        
        Args:
            grid_size: Size of spatial grid (rows, cols)
        """
        self.grid_size = grid_size
        
        # Define state space (position)
        self.state_dim = (grid_size[0], grid_size[1])
        
        # Initialize belief state (uniform distribution)
        self.beliefs = np.ones(self.state_dim) / (grid_size[0] * grid_size[1])
        
        # Define actions
        self.actions = ['up', 'down', 'left', 'right', 'stay']
        
        # Define transition model
        self.transition_matrices = self._initialize_transition_matrices()
        
        # Define observation model
        self.observation_model = self._initialize_observation_model()
        
        # Define preferences (e.g., goal locations)
        self.preferences = np.zeros(self.state_dim)
        
        # Set precision
        self.precision = 1.0
        
    def _initialize_transition_matrices(self):
        """Initialize transition matrices for each action.
        
        Returns:
            Dictionary mapping actions to transition matrices
        """
        matrices = {}
        rows, cols = self.state_dim
        
        # For each action, create a transition matrix
        for action in self.actions:
            # Initialize with zeros
            T = np.zeros((rows, cols, rows, cols))
            
            # Fill in transition probabilities
            for r in range(rows):
                for c in range(cols):
                    if action == 'up':
                        next_r = max(0, r - 1)
                        next_c = c
                    elif action == 'down':
                        next_r = min(rows - 1, r + 1)
                        next_c = c
                    elif action == 'left':
                        next_r = r
                        next_c = max(0, c - 1)
                    elif action == 'right':
                        next_r = r
                        next_c = min(cols - 1, c + 1)
                    else:  # stay
                        next_r = r
                        next_c = c
                    
                    # Set high probability for intended transition
                    T[r, c, next_r, next_c] = 0.8
                    
                    # Add small probability for other transitions
                    for alt_r in range(max(0, next_r-1), min(rows, next_r+2)):
                        for alt_c in range(max(0, next_c-1), min(cols, next_c+2)):
                            if alt_r != next_r or alt_c != next_c:
                                T[r, c, alt_r, alt_c] = 0.2 / 8  # Distribute remaining prob
            
            matrices[action] = T
        
        return matrices
    
    def _initialize_observation_model(self):
        """Initialize observation model.
        
        Returns:
            Observation likelihood matrix
        """
        # Simple model: accurate observations with some noise
        rows, cols = self.state_dim
        O = np.zeros((rows, cols, rows, cols))
        
        for r in range(rows):
            for c in range(cols):
                # Highest probability for true location
                O[r, c, r, c] = 0.9
                
                # Small probability for adjacent locations
                for obs_r in range(max(0, r-1), min(rows, r+2)):
                    for obs_c in range(max(0, c-1), min(cols, c+2)):
                        if (obs_r != r or obs_c != c):
                            O[r, c, obs_r, obs_c] = 0.1 / 8
        
        return O
    
    def set_goal(self, goal_position):
        """Set agent's goal position.
        
        Args:
            goal_position: Tuple (row, col) of goal position
        """
        # Reset preferences
        self.preferences = np.zeros(self.state_dim)
        
        # Set high preference for goal
        self.preferences[goal_position] = 5.0
        
    def update_beliefs(self, observation):
        """Update beliefs based on new observation.
        
        Args:
            observation: Tuple (row, col) of observed position
            
        Returns:
            Updated belief distribution
        """
        rows, cols = self.state_dim
        
        # Initialize likelihood
        likelihood = np.zeros(self.state_dim)
        
        # Compute likelihood of observation given each state
        for r in range(rows):
            for c in range(cols):
                likelihood[r, c] = self.observation_model[r, c, observation[0], observation[1]]
        
        # Bayesian update (posterior ∝ likelihood * prior)
        posterior = likelihood * self.beliefs
        
        # Normalize
        posterior = posterior / np.sum(posterior)
        
        # Update beliefs
        self.beliefs = posterior
        
        return posterior
    
    def calculate_expected_free_energy(self, action):
        """Calculate expected free energy for an action.
        
        Args:
            action: Action to evaluate
            
        Returns:
            Expected free energy value
        """
        rows, cols = self.state_dim
        efe = 0
        
        # Get transition matrix for this action
        T = self.transition_matrices[action]
        
        # For each current state
        for r in range(rows):
            for c in range(cols):
                # Skip if belief is negligible
                if self.beliefs[r, c] < 1e-6:
                    continue
                
                # For each potential next state
                for next_r in range(rows):
                    for next_c in range(cols):
                        # Skip if transition probability is negligible
                        if T[r, c, next_r, next_c] < 1e-6:
                            continue
                        
                        # Probability of this transition
                        p_transition = self.beliefs[r, c] * T[r, c, next_r, next_c]
                        
                        # Expected surprise (negative preference)
                        expected_surprise = -self.preferences[next_r, next_c]
                        
                        # Information gain (epistemic value)
                        # Simplified: use entropy of observation model as proxy
                        info_gain = 0
                        for obs_r in range(rows):
                            for obs_c in range(cols):
                                p_obs = self.observation_model[next_r, next_c, obs_r, obs_c]
                                if p_obs > 0:
                                    info_gain -= p_obs * np.log(p_obs)
                        
                        # Add to expected free energy
                        efe += p_transition * (expected_surprise - info_gain)
        
        return efe
    
    def select_action(self):
        """Select action based on expected free energy.
        
        Returns:
            Selected action
        """
        # Calculate EFE for each action
        efes = {}
        for action in self.actions:
            efes[action] = self.calculate_expected_free_energy(action)
        
        # Convert to array
        efe_values = np.array([efes[a] for a in self.actions])
        
        # Apply softmax with precision
        action_probs = softmax(-self.precision * efe_values)
        
        # Sample action based on probabilities
        action_idx = np.random.choice(len(self.actions), p=action_probs)
        
        return self.actions[action_idx]
    
    def update_precision(self, new_precision):
        """Update action selection precision.
        
        Args:
            new_precision: New precision value
        """
        self.precision = new_precision
```

### Hierarchical Geospatial Application

For a real-world application like urban mobility prediction:

```python
class UrbanMobilityModel:
    def __init__(self):
        """Initialize urban mobility model."""
        # City level (macro)
        self.city_model = SpatialGenerativeModel(resolution=8)
        
        # Neighborhood level (meso)
        self.neighborhood_models = {}
        
        # Individual level (micro)
        self.individual_models = {}
        
    def predict_mobility_patterns(self, observations):
        """Predict mobility patterns at multiple scales.
        
        Args:
            observations: Dictionary of observations at different scales
            
        Returns:
            Predicted mobility patterns at all scales
        """
        # Implementation
```

## Integration with GEO-INFER Modules

### GEO-INFER-ACT

The `GEO-INFER-ACT` module provides core active inference implementations:

```python
from geo_infer_act import GenerativeModel, ActiveInferenceAgent

# Create geospatial generative model
model = GenerativeModel(
    state_type="spatial",
    spatial_resolution=9,
    coordinate_system="EPSG:4326"
)

# Create agent
agent = ActiveInferenceAgent(
    model=model,
    precision=1.0,
    planning_horizon=5
)

# Update beliefs with observations
observations = {
    "temperature": [25.3, 24.8, 26.1],
    "humidity": [65, 68, 62],
    "coordinates": [[lat1, lon1], [lat2, lon2], [lat3, lon3]]
}

updated_beliefs = agent.update_beliefs(observations)

# Select action
action = agent.select_action()
```

### Integration with Other Modules

- **GEO-INFER-SPACE**: Provides spatial representation and operations
- **GEO-INFER-TIME**: Provides temporal dynamics and time series analysis
- **GEO-INFER-SIM**: Uses active inference models for simulation
- **GEO-INFER-AGENT**: Implements multi-agent active inference systems

## Best Practices

### Model Design

1. **Start Simple**
   - Begin with simplified generative models
   - Add complexity incrementally
   - Validate each stage thoroughly

2. **Document Assumptions**
   - Clearly state model assumptions
   - Document state space and action space
   - Explain observation model limitations

3. **Performance Considerations**
   - Use sparse representations for large state spaces
   - Consider approximate inference for complex models
   - Document computational requirements

### Testing and Validation

1. **Sanity Checks**
   - Verify belief updates with simple observations
   - Check policy selection with clear preferences
   - Validate precision effects on exploration/exploitation

2. **Edge Cases**
   - Test with extreme precision values
   - Verify behavior with conflicting observations
   - Check convergence with sparse observations

3. **Real-world Validation**
   - Compare predictions with empirical data
   - Validate on historical geospatial datasets
   - Document prediction accuracy metrics

## Resources

### Key References

1. Friston, K. J., FitzGerald, T., Rigoli, F., Schwartenbeck, P., & Pezzulo, G. (2017). Active inference: A process theory. Neural Computation, 29(1), 1-49.

2. Parr, T., & Friston, K. J. (2018). The anatomy of inference: Generative models and their implications for free energy formulations of active inference. Frontiers in computational neuroscience, 12, 90.

3. Sajid, N., Ball, P. J., & Friston, K. J. (2020). Active inference: Demystified and compared. arXiv preprint arXiv:2009.01865.

### Recommended Libraries

- **PyTorch**: For implementing differentiable generative models
- **JAX**: For gradient-based inference
- **SciPy**: For optimization and probability distributions
- **GeoPandas**: For geospatial data handling
- **Pyro**: For probabilistic programming

## License

This guide is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. 