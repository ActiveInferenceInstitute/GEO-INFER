# GEO-INFER-ANT Test Suite

This directory contains comprehensive tests for the GEO-INFER-ANT swarm intelligence and complex adaptive systems framework.

## Directory Structure

```
tests/
├── __init__.py                    # Test package initialization
├── test_aco.py                   # Ant Colony Optimization tests
├── test_algorithms.py            # General algorithm tests
├── test_core.py                  # Core component tests
├── test_population.py            # Population dynamics tests
├── test_stigmergy.py             # Stigmergic communication tests
└── test_applications.py          # Application-specific tests
```

## Test Categories

### Core Component Tests

**File**: `test_core.py`

Tests fundamental swarm components:

```python
def test_swarm_agent_creation():
    """Test basic swarm agent initialization"""
    agent = SwarmAgent(
        agent_id="test_ant_001",
        position=np.array([37.7749, -122.4194]),
        sensory_range=100.0
    )

    assert agent.agent_id == "test_ant_001"
    assert np.allclose(agent.position, [37.7749, -122.4194])
    assert agent.sensory_range == 100.0

def test_agent_sensory_processing():
    """Test agent sensory input processing"""
    agent = SwarmAgent(...)

    sensory_input = {
        'pheromone_trails': [{'type': 'food', 'intensity': 0.8, 'direction': 45}],
        'nearby_agents': [{'id': 'ant_002', 'distance': 50}],
        'environmental_data': {'temperature': 25.0, 'humidity': 0.6}
    }

    processed_input = agent.perceive_environment(
        spatial_context=current_location,
        signals=sensory_input
    )

    assert 'pheromone_signals' in processed_input
    assert 'agent_proximity' in processed_input
    assert processed_input['processed'] is True
```

### Population Dynamics Tests

**File**: `test_population.py`

Tests agent population management:

```python
def test_population_initialization():
    """Test agent population creation"""
    population = AgentPopulation(
        population_size=100,
        agent_types=['worker', 'scout'],
        spatial_distribution='clustered'
    )

    assert len(population.agents) == 100
    assert population.agent_types == ['worker', 'scout']

    # Check spatial distribution
    positions = [agent.position for agent in population.agents]
    assert is_clustered_distribution(positions)

def test_population_simulation():
    """Test population dynamics simulation"""
    population = AgentPopulation(population_size=50)

    # Configure environmental dynamics
    environment = population.initialize_environment(
        spatial_bounds=geographic_area,
        resource_distribution=food_sources
    )

    # Run simulation
    simulation_results = population.run_simulation(
        time_steps=100,
        data_collection=['trajectories', 'interactions']
    )

    assert len(simulation_results['trajectories']) == 50
    assert 'interactions' in simulation_results
    assert simulation_results['time_steps'] == 100
```

### Stigmergy Tests

**File**: `test_stigmergy.py`

Tests indirect communication mechanisms:

```python
def test_pheromone_deposition():
    """Test pheromone deposition by agents"""
    pheromone_system = PheromoneSystem(
        spatial_resolution='h3_r8',
        evaporation_rate=0.1
    )

    agent = SwarmAgent(position=test_position)

    # Agent deposits pheromone
    agent.deposit_pheromone(
        pheromone_type='trail',
        intensity=1.0,
        location=agent.position
    )

    # Check pheromone presence
    pheromones = pheromone_system.get_pheromones_at_location(agent.position)
    assert 'trail' in pheromones
    assert pheromones['trail'] > 0.8  # Should not have evaporated much

def test_pheromone_diffusion():
    """Test pheromone diffusion over time"""
    pheromone_system = PheromoneSystem(evaporation_rate=0.1)

    # Deposit initial pheromone
    initial_intensity = 1.0
    pheromone_system.deposit_pheromone(
        location=test_location,
        pheromone_type='food',
        intensity=initial_intensity
    )

    # Simulate time passage
    time_steps = 10
    for _ in range(time_steps):
        pheromone_system.update_pheromones(time_delta=1.0)

    # Check evaporation
    final_intensity = pheromone_system.get_pheromone_intensity(
        location=test_location,
        pheromone_type='food'
    )

    expected_intensity = initial_intensity * (1 - 0.1) ** time_steps
    assert abs(final_intensity - expected_intensity) < 0.01
```

### Algorithm Tests

**File**: `test_aco.py`

Tests Ant Colony Optimization:

```python
def test_aco_convergence():
    """Test ACO convergence on optimization problem"""
    aco = AntColonyOptimization(
        number_of_ants=20,
        pheromone_evaporation=0.1,
        iterations=50
    )

    # Solve traveling salesman problem
    optimal_route = aco.optimize_route(
        locations=city_coordinates,
        distance_matrix=travel_distances
    )

    assert len(optimal_route) == len(city_coordinates)
    assert is_valid_route(optimal_route, distance_matrix)

    # Check convergence
    final_solution_quality = calculate_route_length(optimal_route, distance_matrix)
    assert final_solution_quality < initial_solution_quality

def test_pheromone_update():
    """Test pheromone trail updating"""
    aco = AntColonyOptimization()

    # Simulate ant traversal
    route = [0, 1, 2, 3, 0]  # Cycle route
    route_length = calculate_route_length(route, distance_matrix)

    aco.update_pheromones(route, route_length)

    # Check pheromone levels on route edges
    for i in range(len(route) - 1):
        edge = (route[i], route[i+1])
        pheromone_level = aco.get_pheromone_level(edge)
        assert pheromone_level > aco.initial_pheromone
```

**File**: `test_algorithms.py`

General algorithm testing:

```python
def test_pso_optimization():
    """Test Particle Swarm Optimization"""
    pso = ParticleSwarmOptimization(
        swarm_size=30,
        dimensions=2,
        bounds=[(-10, 10), (-10, 10)]
    )

    optimal_solution = pso.optimize(
        objective_function=sphere_function,
        max_iterations=100
    )

    assert len(optimal_solution) == 2
    assert all(-10 <= x <= 10 for x in optimal_solution)

    # Check convergence to global optimum (0, 0) for sphere function
    distance_from_optimum = np.linalg.norm(optimal_solution)
    assert distance_from_optimum < 0.1

def test_abc_algorithm():
    """Test Artificial Bee Colony algorithm"""
    abc = ArtificialBeeColony(
        colony_size=50,
        dimensions=3,
        bounds=[(-5, 5)] * 3
    )

    solution = abc.optimize(
        objective_function=rosenbrock_function,
        max_iterations=200
    )

    assert len(solution) == 3
    fitness = rosenbrock_function(solution)
    assert fitness < 1.0  # Should find good solution
```

### Application Tests

**File**: `test_applications.py`

Tests domain-specific applications:

```python
def test_environmental_monitoring():
    """Test environmental monitoring swarm application"""
    env_swarm = EnvironmentalMonitoringSwarm(
        swarm_size=20,
        monitoring_targets=['air_quality', 'temperature']
    )

    # Deploy monitoring agents
    deployment = env_swarm.deploy_agents(
        spatial_coverage=test_area,
        environmental_priorities=pollution_sources
    )

    assert len(deployment['agents']) == 20
    assert all('position' in agent for agent in deployment['agents'])

    # Test monitoring coordination
    monitoring_results = env_swarm.coordinate_monitoring(
        agent_positions=deployment['agents'],
        time_window=3600  # 1 hour
    )

    assert 'air_quality_readings' in monitoring_results
    assert 'temperature_readings' in monitoring_results

def test_disaster_response():
    """Test disaster response coordination"""
    response_swarm = DisasterResponseSwarm(
        response_types=['search', 'rescue'],
        swarm_size=15
    )

    # Assess disaster situation
    assessment = response_swarm.assess_situation(
        disaster_area=affected_region,
        incident_severity='high',
        available_resources=response_assets
    )

    assert assessment['severity'] == 'high'
    assert 'resource_requirements' in assessment

    # Coordinate response
    coordination = response_swarm.coordinate_response(
        situation_assessment=assessment,
        time_available=7200,  # 2 hours
        coordination_objective='maximize_coverage'
    )

    assert len(coordination['assigned_tasks']) > 0
    assert 'communication_network' in coordination
```

## Running Tests

### Basic Execution

```bash
# Run all tests
python -m pytest tests/

# Run specific algorithm tests
python -m pytest tests/test_aco.py

# Run with verbose output
python -m pytest -v tests/
```

### Performance Testing

```bash
# Run performance benchmarks
python -m pytest --benchmark-only tests/

# Profile specific test
python -m pytest --profile tests/test_algorithms.py::test_pso_optimization
```

### Coverage Analysis

```bash
# Generate coverage report
python -m pytest --cov=geo_infer_ant --cov-report=html tests/

# Check coverage thresholds
python -m pytest --cov=geo_infer_ant --cov-report=term-missing --cov-fail-under=90 tests/
```

## Test Configuration

### Fixtures

Common test fixtures:

```python
@pytest.fixture
def sample_swarm_agent():
    """Provide sample swarm agent"""
    return SwarmAgent(
        agent_id="test_agent",
        position=np.array([0.0, 0.0]),
        sensory_range=50.0
    )

@pytest.fixture
def test_population():
    """Provide test agent population"""
    return AgentPopulation(
        population_size=20,
        spatial_distribution='random'
    )

@pytest.fixture
def pheromone_system():
    """Provide test pheromone system"""
    return PheromoneSystem(
        evaporation_rate=0.05,
        diffusion_rate=0.1
    )
```

### Test Data Generation

```python
def generate_city_coordinates(n_cities=10):
    """Generate random city coordinates"""
    return np.random.uniform(-180, 180, (n_cities, 2))

def create_distance_matrix(coordinates):
    """Create Euclidean distance matrix"""
    n = len(coordinates)
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i, j] = np.linalg.norm(coordinates[i] - coordinates[j])
    return distances

def generate_spatial_environment(bounds, n_resources=5):
    """Generate test spatial environment"""
    return {
        'bounds': bounds,
        'resources': np.random.uniform(bounds[0], bounds[1], (n_resources, 2)),
        'obstacles': []
    }
```

## Performance Benchmarks

### Algorithm Benchmarks

```python
def test_aco_performance_scaling(benchmark):
    """Benchmark ACO performance with problem size"""
    sizes = [10, 20, 30, 50]

    for size in sizes:
        coordinates = generate_city_coordinates(size)
        distances = create_distance_matrix(coordinates)

        aco = AntColonyOptimization(number_of_ants=min(20, size))

        result = benchmark(
            aco.optimize_route,
            coordinates,
            distances
        )

        assert result['convergence'] is True
        assert result['solution_quality'] > 0
```

### Swarm Benchmarks

```python
def test_population_simulation_performance(benchmark):
    """Benchmark population simulation speed"""
    population_sizes = [50, 100, 200]

    for size in population_sizes:
        population = AgentPopulation(population_size=size)

        result = benchmark(
            population.run_simulation,
            time_steps=100,
            data_collection=['positions']
        )

        assert result['completed'] is True
        assert len(result['trajectories']) == size
```

## Test Coverage Goals

- **Core Components**: >95% coverage
- **Algorithms**: >90% coverage each
- **Applications**: >85% coverage each
- **Integration Tests**: Cover major workflows
- **Performance Tests**: Benchmark critical operations

## Writing New Tests

### Test Structure Template

```python
import pytest
import numpy as np
from geo_infer_ant.core.agent_base import SwarmAgent

class TestSwarmAgent:
    """Test swarm agent functionality"""

    @pytest.fixture
    def sample_agent(self):
        """Create sample agent for testing"""
        return SwarmAgent(
            agent_id="test_agent",
            position=np.array([0.0, 0.0]),
            sensory_range=50.0
        )

    def test_agent_initialization(self, sample_agent):
        """Test agent creation"""
        assert sample_agent.agent_id == "test_agent"
        assert np.allclose(sample_agent.position, [0.0, 0.0])
        assert sample_agent.sensory_range == 50.0

    def test_sensory_processing(self, sample_agent):
        """Test sensory input processing"""
        sensory_input = {
            'nearby_agents': [{'id': 'agent_2', 'distance': 30}],
            'environmental_signals': {'resource': 0.8}
        }

        processed = sample_agent.perceive_environment(
            spatial_context=sample_agent.position,
            signals=sensory_input
        )

        assert 'processed_signals' in processed
        assert processed['agent_detected'] is True

    def test_decision_making(self, sample_agent):
        """Test agent decision making"""
        sensory_input = {'food_source': {'direction': 45, 'intensity': 0.9}}

        decision = sample_agent.make_decision(
            sensory_input=sensory_input,
            motivations={'forage': 0.8},
            behavioral_rules=test_rules
        )

        assert 'action' in decision
        assert decision['action'] in ['move_toward_food', 'recruit_others', 'ignore']
```

## Debugging and Troubleshooting

### Common Issues

1. **Numerical Instability**: Check swarm parameters and bounds
2. **Convergence Problems**: Verify algorithm parameters and stopping criteria
3. **Memory Issues**: Monitor population sizes in large simulations
4. **Spatial Index Errors**: Validate coordinate systems and bounds

### Debugging Tools

```bash
# Run with debugging
python -m pytest --pdb tests/test_core.py::TestSwarmAgent::test_decision_making

# Run with detailed output
python -m pytest -s -v tests/

# Profile memory usage
python -m pytest --profile-svg tests/test_population.py::test_large_simulation
```

## Contributing

1. Add tests for new algorithms before implementation
2. Include performance benchmarks for optimization algorithms
3. Maintain comprehensive test coverage (>85%)
4. Add integration tests for new applications
5. Update this README for new test categories

