# GEO-INFER-ANT Source Code

This directory contains the core implementation of the GEO-INFER-ANT swarm intelligence and complex adaptive systems framework.

## Directory Structure

```
src/
├── geo_infer_ant/
│   ├── __init__.py                    # Package initialization
│   ├── core/                         # Core swarm intelligence components
│   │   ├── __init__.py
│   │   ├── agent_base.py             # Base agent classes
│   │   ├── population.py             # Agent population management
│   │   ├── stigmergy.py              # Stigmergic communication
│   │   └── digital_stigmergy.py      # Digital stigmergy systems
│   ├── algorithms/                   # Swarm optimization algorithms
│   │   ├── __init__.py
│   │   ├── aco.py                    # Ant Colony Optimization
│   │   ├── pso.py                    # Particle Swarm Optimization
│   │   └── abc.py                    # Artificial Bee Colony
│   ├── applications/                 # Domain-specific applications
│   │   ├── __init__.py
│   │   ├── environmental.py          # Environmental monitoring
│   │   ├── disaster.py               # Disaster response
│   │   └── urban.py                  # Urban optimization
│   └── analysis/                     # Analysis and evaluation tools
│       ├── __init__.py
│       ├── patterns.py               # Pattern recognition
│       └── metrics.py                # Performance metrics
```

## Core Components

### Agent Base Classes

**Location**: `core/agent_base.py`

Foundation classes for swarm agents:

```python
from geo_infer_ant.core.agent_base import SwarmAgent

class SwarmAgent:
    """Base class for swarm intelligence agents"""

    def __init__(self, agent_id, position, sensory_range=100.0):
        self.agent_id = agent_id
        self.position = position
        self.sensory_range = sensory_range
        self.internal_state = {}

    def perceive_environment(self, spatial_context, signals):
        """Process environmental inputs"""
        raise NotImplementedError

    def make_decision(self, sensory_input, motivations):
        """Make behavioral decisions"""
        raise NotImplementedError

    def execute_action(self, decision):
        """Execute chosen action"""
        raise NotImplementedError

    def communicate(self, message, recipients):
        """Communicate with other agents"""
        raise NotImplementedError
```

### Population Dynamics

**Location**: `core/population.py`

Manages collections of interacting agents:

```python
from geo_infer_ant.core.population import AgentPopulation

# Initialize agent population
population = AgentPopulation(
    population_size=1000,
    agent_types=['worker', 'scout', 'soldier'],
    spatial_distribution='random_clustered'
)

# Configure behavioral rules
population.set_behavioral_rules(
    foraging_strategy=foraging_rules,
    communication_protocol=interaction_rules,
    adaptation_mechanisms=learning_rules
)

# Run population simulation
simulation = population.run_simulation(
    time_steps=1000,
    environmental_dynamics=seasonal_changes,
    data_collection=['trajectories', 'interactions', 'emergent_behaviors']
)
```

### Stigmergic Communication

**Location**: `core/stigmergy.py`

Implements indirect communication through environmental modification:

```python
from geo_infer_ant.core.stigmergy import PheromoneSystem

# Initialize pheromone-based communication
pheromone_system = PheromoneSystem(
    spatial_resolution='h3_r8',
    pheromone_types=['trail', 'food', 'alarm', 'nest'],
    evaporation_rate=0.1,
    diffusion_model='gaussian'
)

# Agent deposits pheromone
agent.deposit_pheromone(
    pheromone_type='trail',
    intensity=1.0,
    location=current_position,
    persistence_time=300  # seconds
)

# Environmental pheromone dynamics
pheromone_system.update_pheromones(
    time_delta=1.0,
    environmental_factors={'wind_speed': 5.0, 'temperature': 25.0}
)

# Agent senses pheromones
detected_signals = agent.sense_pheromones(
    location=current_position,
    sensory_range=50.0,
    pheromone_types=['trail', 'food']
)
```

## Optimization Algorithms

### Ant Colony Optimization

**Location**: `algorithms/aco.py`

Path optimization and combinatorial problem solving:

```python
from geo_infer_ant.algorithms.aco import AntColonyOptimization

aco = AntColonyOptimization(
    number_of_ants=50,
    pheromone_evaporation=0.1,
    pheromone_intensity=1.0,
    alpha=1.0,  # pheromone influence
    beta=2.0    # heuristic influence
)

# Solve traveling salesman problem
optimal_route = aco.optimize_route(
    locations=city_coordinates,
    distance_matrix=travel_distances,
    start_location=depot,
    constraints={'max_distance': 1000, 'time_window': (8, 18)}
)

# Multi-objective optimization
pareto_solutions = aco.multi_objective_optimization(
    objectives=['minimize_cost', 'minimize_time', 'maximize_service'],
    problem_instance=logistics_problem,
    population_size=100
)
```

### Particle Swarm Optimization

**Location**: `algorithms/pso.py`

Continuous optimization using swarm intelligence:

```python
from geo_infer_ant.algorithms.pso import ParticleSwarmOptimization

pso = ParticleSwarmOptimization(
    swarm_size=100,
    dimensions=2,  # spatial optimization
    bounds=[(lat_min, lat_max), (lon_min, lon_max)],
    inertia_weight=0.7,
    cognitive_acceleration=1.5,
    social_acceleration=1.5
)

# Optimize spatial configuration
optimal_locations = pso.optimize(
    objective_function=spatial_fitness_function,
    initial_positions=random_initialization,
    velocity_bounds=movement_constraints,
    convergence_threshold=1e-6
)

# Dynamic adaptation
pso.adapt_to_environment(
    environmental_changes=new_obstacles,
    performance_feedback=optimization_history,
    adaptation_rate=0.1
)
```

### Artificial Bee Colony

**Location**: `algorithms/abc.py`

Nature-inspired optimization algorithm:

```python
from geo_infer_ant.algorithms.abc import ArtificialBeeColony

abc = ArtificialBeeColony(
    colony_size=100,
    employed_bees_ratio=0.5,
    scout_bees_ratio=0.1,
    max_trials=50,  # abandonment threshold
    limit=100       # maximum trials before abandonment
)

# Optimize complex function
optimal_solution = abc.optimize(
    objective_function=complex_fitness_function,
    search_space=parameter_bounds,
    max_iterations=1000,
    convergence_criterion='improvement_threshold'
)

# Adaptive foraging
abc.adapt_foraging_strategy(
    problem_characteristics=function_landscape,
    colony_performance=convergence_metrics,
    environmental_conditions=constraint_changes
)
```

## Domain Applications

### Environmental Monitoring

**Location**: `applications/environmental.py`

Swarm-based environmental monitoring systems:

```python
from geo_infer_ant.applications.environmental import EnvironmentalSwarm

env_swarm = EnvironmentalSwarm(
    swarm_size=200,
    monitoring_targets=['air_quality', 'water_quality', 'biodiversity'],
    spatial_coverage=target_region,
    adaptive_sampling=True
)

# Deploy monitoring agents
deployment_plan = env_swarm.deploy_agents(
    initial_positions=base_stations,
    environmental_priorities=pollution_hotspots,
    logistical_constraints=terrain_accessibility
)

# Coordinate monitoring activities
coordinated_monitoring = env_swarm.coordinate_monitoring(
    agent_positions=current_locations,
    environmental_conditions=weather_data,
    data_requirements=information_needs,
    resource_constraints=battery_levels
)
```

### Disaster Response

**Location**: `applications/disaster.py`

Coordinated disaster response using swarm intelligence:

```python
from geo_infer_ant.applications.disaster import DisasterResponseSwarm

response_swarm = DisasterResponseSwarm(
    response_types=['search_rescue', 'damage_assessment', 'supply_distribution'],
    swarm_composition={'drones': 20, 'vehicles': 15, 'personnel': 10},
    coordination_protocol='stigmergic',
    real_time_adaptation=True
)

# Assess disaster situation
situation_assessment = response_swarm.assess_situation(
    disaster_type='earthquake',
    affected_area=impact_zone,
    available_assets=response_resources,
    environmental_conditions=field_hazards
)

# Coordinate response efforts
response_coordination = response_swarm.coordinate_response(
    assessment=situation_assessment,
    priorities=incident_severity,
    resource_allocation=optimal_deployment,
    communication_networks=available_channels
)
```

### Urban Optimization

**Location**: `applications/urban.py`

Urban systems optimization using swarm intelligence:

```python
from geo_infer_ant.applications.urban import UrbanOptimizationSwarm

urban_swarm = UrbanOptimizationSwarm(
    optimization_targets=['traffic_flow', 'energy_distribution', 'waste_collection'],
    spatial_scale='city_district',
    temporal_resolution='real_time',
    stakeholder_objectives=['efficiency', 'sustainability', 'equity']
)

# Optimize urban systems
optimization_results = urban_swarm.optimize_urban_systems(
    current_state=city_conditions,
    performance_objectives=target_metrics,
    resource_constraints=budget_limits,
    environmental_factors=weather_traffic_data
)

# Adaptive management
adaptive_management = urban_swarm.adaptive_management(
    system_performance=real_time_metrics,
    environmental_changes=weather_events,
    stakeholder_feedback=public_input,
    learning_rate=0.05
)
```

## Analysis Tools

### Pattern Recognition

**Location**: `analysis/patterns.py`

Analysis of emergent patterns in swarm behavior:

```python
from geo_infer_ant.analysis.patterns import SwarmPatternAnalyzer

pattern_analyzer = SwarmPatternAnalyzer(
    pattern_types=['spatial_clustering', 'temporal_synchronization', 'phase_transitions'],
    statistical_methods=['cluster_analysis', 'network_analysis', 'fractal_analysis']
)

# Analyze spatial patterns
spatial_patterns = pattern_analyzer.analyze_spatial_patterns(
    agent_trajectories=position_data,
    pattern_types=['flocking', 'swarming', 'migration'],
    spatial_scale=analysis_resolution,
    temporal_window=behavior_period
)

# Detect emergent phenomena
emergent_behaviors = pattern_analyzer.detect_emergence(
    individual_actions=agent_behaviors,
    collective_outcomes=system_behavior,
    information_measures=['mutual_information', 'transfer_entropy'],
    complexity_measures=['fractal_dimension', 'correlation_dimension']
)
```

### Performance Metrics

**Location**: `analysis/metrics.py`

Evaluation of swarm algorithm performance:

```python
from geo_infer_ant.analysis.metrics import SwarmPerformanceMetrics

performance_evaluator = SwarmPerformanceMetrics(
    evaluation_criteria=['convergence_speed', 'solution_quality', 'robustness', 'scalability'],
    benchmark_datasets=standard_test_cases,
    statistical_analysis=['hypothesis_testing', 'confidence_intervals']
)

# Evaluate algorithm performance
performance_assessment = performance_evaluator.evaluate_performance(
    algorithm_results=optimization_history,
    problem_instances=test_problems,
    computational_resources=hardware_specs,
    comparison_baselines=alternative_methods
)

# Analyze robustness
robustness_analysis = performance_evaluator.analyze_robustness(
    failure_scenarios=['agent_failures', 'communication_disruptions', 'environmental_changes'],
    recovery_mechanisms=['redundancy', 'adaptation', 'reorganization'],
    performance_degradation=acceptable_limits
)
```

## Development Guidelines

### Adding New Algorithms

1. Create algorithm class in `algorithms/` directory
2. Extend base algorithm interface
3. Implement core optimization logic
4. Add convergence criteria and stopping conditions
5. Include parameter adaptation mechanisms

### Adding New Applications

1. Create application class in `applications/` directory
2. Define domain-specific problem formulation
3. Implement swarm-based solution approach
4. Add domain-specific constraints and objectives
5. Include validation against real-world data

### Code Style and Testing

- Follow PEP 8 conventions
- Include comprehensive docstrings
- Write unit tests for all algorithms
- Include performance benchmarks
- Document algorithmic parameters and assumptions

Run tests:
```bash
python -m pytest tests/
```

Run performance benchmarks:
```bash
python -m pytest tests/ --benchmark-only
```

## Dependencies

- `numpy`: Numerical computations
- `scipy`: Scientific computing
- `matplotlib`: Visualization
- `networkx`: Graph algorithms
- `geopandas`: Geospatial data handling
- `h3`: H3 spatial indexing (optional)

## Integration Points

The ANT module integrates with:

- **GEO-INFER-SPACE**: Spatial reasoning and H3 indexing
- **GEO-INFER-TIME**: Temporal dynamics and scheduling
- **GEO-INFER-ACT**: Active Inference for individual agents
- **GEO-INFER-AGENT**: Agent lifecycle management
- **GEO-INFER-SIM**: Simulation environments
- **GEO-INFER-OPT**: Optimization problem formulations
