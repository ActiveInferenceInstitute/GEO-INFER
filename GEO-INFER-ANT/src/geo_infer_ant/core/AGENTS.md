# Agent
: core

## Scope
 This directory contains core components for the module. It provides 14 classes and 1 functions.

## Classes
 and Functions

### SensoryInput
 Structured sensory input for swarm agents.

**Methods**:
- `process() -> Dict[str, Any]`: Process and integrate all sensory inputs.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary representation.

### ActionDecision
 Structured action decision for swarm agents.

**Methods**:
- `calculate_priority() -> float`: Calculate execution priority based on confidence and context.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary representation.

### SwarmAgent
 Base class for swarm intelligence agents.

**Methods**:
- `make_decision(sensory_input: SensoryInput, internal_motivations: Optional[Dict[str, float]], behavioral_rules: Optional[Dict[str, Any]]) -> ActionDecision`: Make behavioral decision based on sensory input and internal state.
- `update_beliefs(perception: Dict[str, Any]) -> None`: Update beliefs based on perception.
- `to_dict() -> Dict[str, Any]`: Convert agent to dictionary representation.

### DigitalTrace
 Digital information trace left by agents in the environment.

**Methods**:
- `is_expired() -> bool`: Check if trace has exceeded its persistence duration.
- `get_credibility_weight() -> float`: Get credibility-weighted value for decision making.
- `to_dict() -> Dict[str, Any]`: Convert trace to dictionary representation.

### InformationQuery
 Query for digital stigmergic information.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert query to dictionary representation.

### DigitalStigmergy
 Digital stigmergy system for agent coordination.

**Methods**:
- `get_system_statistics() -> Dict[str, Any]`: Get system statistics.
- `save_digital_traces(filepath: str) -> bool`: Save digital traces to file.
- `load_digital_traces(filepath: str) -> bool`: Load digital traces from file.

### PopulationConfig
 Configuration for agent population dynamics.

### EnvironmentalState
 Current state of the simulation environment.

**Methods**:
- `update_environmental_factors(factors: Dict[str, Any]) -> None`: Update environmental factors.
- `get_resource_at_location(location: np.ndarray) -> Dict[str, Any]`: Get resources available at a specific location.

### SimulationResults
 Results from population dynamics simulation.

**Methods**:
- `add_trajectory(step: int, positions: np.ndarray) -> None`: Add trajectory data for a simulation step.
- `add_interaction(interaction: Dict[str, Any]) -> None`: Add agent interaction data.
- `update_emergent_patterns(patterns: Dict[str, Any]) -> None`: Update emergent pattern analysis.
- `update_performance_metrics(metrics: Dict[str, Any]) -> None`: Update performance metrics.
- `to_dict() -> Dict[str, Any]`: Convert results to dictionary.

### AgentPopulation
 Management system for collections of interacting swarm agents.

**Methods**:
- `set_behavioral_rules(foraging_rules: Optional[Dict[str, Any]], communication_rules: Optional[Dict[str, Any]], adaptation_rules: Optional[Dict[str, Any]]) -> None`: Configure behavioral rules for the population.
- `initialize_environment(spatial_bounds: Optional[Dict[str, float]], resource_distribution: Optional[Dict[str, Any]], obstacle_map: Optional[Dict[str, Any]], pheromone_diffusion: Optional[Dict[str, Any]], environmental_factors: Optional[Dict[str, Any]]) -> EnvironmentalState`: Initialize the spatial environment for agent simulation.
- `create_agents() -> List['SwarmAgent']`: Create and initialize all agents in the population.
- `get_agent_by_id(agent_id: str) -> Optional['SwarmAgent']`: Get agent by ID.
- `get_agents_by_type(agent_type: str) -> List['SwarmAgent']`: Get all agents of specified type.
- `get_agents_in_region(center: np.ndarray, radius: float) -> List['SwarmAgent']`: Get all agents within specified radius of center.
- `save_simulation_results(filepath: str) -> None`: Save simulation results to file.
- `load_simulation_results(filepath: str) -> SimulationResults`: Load simulation results from file.

### PheromoneType
 Configuration for a specific pheromone type.

### PheromoneDeposit
 Record of a pheromone deposit by an agent.

### PheromoneField
 Spatial field representing pheromone concentrations.

**Methods**:
- `get_concentration(location: np.ndarray) -> float`: Get pheromone concentration at specific location.

### PheromoneSystem
 pheromone-based stigmergic communication system.

**Methods**:
- `get_pheromone_intensity(location: np.ndarray, pheromone_type: str) -> float`: Get pheromone intensity at specific location.
- `get_pheromone_gradient(location: np.ndarray, pheromone_type: str, radius: float) -> Tuple[float, np.ndarray]`: Get pheromone gradient (intensity and direction) at location.
- `find_strongest_trail(start_location: np.ndarray, pheromone_type: str, search_radius: float) -> Optional[Dict[str, Any]]`: Find the strongest pheromone trail within search radius.
- `get_field_statistics(pheromone_type: str) -> Dict[str, Any]`: Get statistical summary of pheromone field.
- `clear_pheromone_field(pheromone_type: str) -> bool`: Clear all pheromones of specified type.
- `get_performance_statistics() -> Dict[str, Any]`: Get performance statistics for the pheromone system.
- `save_pheromone_fields(filepath: str) -> bool`: Save pheromone fields to file.
- `load_pheromone_fields(filepath: str) -> bool`: Load pheromone fields from file.

### update_single_agent
 `update_single_agent(agent)` Update a single agent (for parallel execution).

## Capabilities

- **14 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-ANT/src/geo_infer_ant/core`
- **Type**: Directory Node
