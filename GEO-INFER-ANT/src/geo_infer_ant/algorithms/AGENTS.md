# Agent
: algorithms ## Scope
 This directory contains algorithms components for the module. It provides 9 classes and 0 functions. ## Classes
 and Functions ### ABCParameter
s
 Parameters for Artificial Bee Colony algorithm. ### FoodSourc
e
 Represents a food source (solution) in the ABC algorithm. **Methods**: - `update_fitness(fitness: float) -> None`: Update fitness and trial count. ### ArtificialBeeColon
y
 Artificial Bee Colony optimization algorithm. **Methods**: - `optimize(objective_function: Callable[[np.ndarray], float], max_iterations: Optional[int], spatial_constraints: Optional[Dict[str, Any]], parallel_computation: bool) -> np.ndarray`: Optimize using Artificial Bee Colony algorithm. - `manage_food_sources(current_sources: List[FoodSource], abandonment_criteria: str, recruitment_strategy: str, spatial_clustering: bool) -> Dict[str, Any]`: Manage food sources with strategies. - `adapt_foraging_strategy(environmental_conditions: Dict[str, Any], colony_performance: Dict[str, Any], behavioral_adaptation: str) -> Dict[str, Any]`: Adapt foraging strategy based on environmental conditions and performance. - `get_optimization_statistics() -> Dict[str, Any]`: Get optimization statistics. ### ACOParameter
s
 Parameters for Ant Colony Optimization algorithm. ### OptimizationResul
t
 Result of ACO optimization. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert result to dictionary. ### AntColonyOptimizatio
n
 Ant Colony Optimization algorithm implementation. **Methods**: - `initialize_problem(nodes: List[Any], distance_matrix: Optional[np.ndarray], heuristic_matrix: Optional[np.ndarray], constraints: Optional[Dict[str, Any]]) -> None`: Initialize the optimization problem. - `optimize_paths(start_locations: List[np.ndarray], end_locations: List[np.ndarray], objective_function: str, constraints: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]`: Optimize paths between multiple start and end locations. - `solve() -> OptimizationResult`: Solve the optimization problem using ACO. - `multi_objective_optimization(objectives: List[str], population_size: int, generations: int, spatial_constraints: Optional[Dict[str, Any]]) -> Dict[str, Any]`: Perform multi-objective optimization using ACO. - `adapt_to_changes(environmental_changes: Dict[str, Any], pheromone_update_strategy: str, convergence_monitoring: bool) -> Dict[str, Any]`: Adapt ACO algorithm to environmental changes. - `get_optimization_statistics() -> Dict[str, Any]`: Get optimization statistics. - `save_optimization_state(filepath: str) -> bool`: Save optimization state to file. - `load_optimization_state(filepath: str) -> bool`: Load optimization state from file. ### PSOParameter
s
 Parameters for Particle Swarm Optimization algorithm. ### Particl
e
 Individual particle in the PSO swarm. **Methods**: - `update_personal_best() -> None`: Update personal best if current fitness is better. - `update_velocity(global_best_position: np.ndarray, inertia_weight: float, cognitive_acceleration: float, social_acceleration: float, neighborhood_best_position: Optional[np.ndarray]) -> None`: Update particle velocity using PSO formula. - `update_position(bounds: List[Tuple[float, float]]) -> None`: Update particle position based on velocity. ### ParticleSwarmOptimizatio
n
 Particle Swarm Optimization algorithm implementation. **Methods**: - `initialize_swarm(initial_positions: Optional[np.ndarray]) -> None`: Initialize the particle swarm. - `optimize(objective_function: Callable[[np.ndarray], float], initial_positions: Optional[np.ndarray], velocity_bounds: Optional[Tuple[float, float]], convergence_criteria: Optional[Dict[str, Any]]) -> np.ndarray`: Optimize the objective function using PSO. - `coordinate_swarms(sub_swarms: List['ParticleSwarmOptimization'], communication_topology: str, information_sharing: str) -> Dict[str, Any]`: Coordinate multiple PSO swarms for complex optimization. - `adapt_parameters(performance_history: List[Dict[str, Any]], environmental_changes: Dict[str, Any], adaptation_strategy: str) -> Dict[str, Any]`: Adapt PSO parameters based on performance and environmental changes. - `get_optimization_statistics() -> Dict[str, Any]`: Get optimization statistics. - `save_optimization_state(filepath: str) -> bool`: Save optimization state to file. - `load_optimization_state(filepath: str) -> bool`: Load optimization state from file. ## Capabilities
 - **9 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-ANT/src/geo_infer_ant/algorithms` - **Type**: Directory Node 