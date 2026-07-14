"""
Ant Colony Optimization (ACO) Algorithm for GEO-INFER-ANT

This module implements the Ant Colony Optimization algorithm, a metaheuristic
inspired by the foraging behavior of ants. The algorithm uses pheromone trails
to find optimal solutions to combinatorial optimization problems, particularly
effective for spatial routing and pathfinding problems.

Key Features:
- Multi-objective optimization support
- Spatial constraint handling
- Dynamic environment adaptation
- Integration with pheromone systems
- Real-time optimization capabilities
- Multiple ACO variants (AS, ACS, MMAS)
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Integration imports
try:
    from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface
    from geo_infer_space.core.analytics import SpatialAnalyticsInterface
except ImportError as e:
    logging.getLogger(__name__).debug("Optional spatial integration unavailable: %s", e)
    SpatialIndexingInterface = None
    SpatialAnalyticsInterface = None

logger = logging.getLogger(__name__)


@dataclass
class ACOParameters:
    """Parameters for Ant Colony Optimization algorithm."""

    number_of_ants: int = 50
    pheromone_evaporation_rate: float = 0.1
    pheromone_deposition_amount: float = 1.0
    alpha: float = 1.0  # Pheromone influence parameter
    beta: float = 2.0  # Heuristic influence parameter
    initial_pheromone: float = 1.0
    max_iterations: int = 100
    convergence_threshold: float = 0.001
    exploration_rate: float = 0.1

    # Advanced parameters
    elitist_ants: int = 0  # Number of elitist ants (ACS variant)
    pheromone_persistence: float = 0.9  # MMAS variant
    min_pheromone: float = 0.01  # MMAS variant
    max_pheromone: float = 10.0  # MMAS variant

    def __post_init__(self):
        """Validate parameters after initialization."""
        if self.number_of_ants <= 0:
            raise ValueError("Number of ants must be positive")
        if not 0 < self.pheromone_evaporation_rate <= 1:
            raise ValueError("Evaporation rate must be between 0 and 1")
        if self.alpha <= 0 or self.beta <= 0:
            raise ValueError("Alpha and beta must be positive")


@dataclass
class OptimizationResult:
    """Result of ACO optimization."""

    best_solution: List[Any]
    best_fitness: float
    convergence_history: List[float] = field(default_factory=list)
    pheromone_history: List[Dict[str, float]] = field(default_factory=list)
    computation_time: float = 0.0
    iterations_completed: int = 0
    convergence_achieved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "best_solution": self.best_solution,
            "best_fitness": self.best_fitness,
            "convergence_history": self.convergence_history,
            "pheromone_history": self.pheromone_history,
            "computation_time": self.computation_time,
            "iterations_completed": self.iterations_completed,
            "convergence_achieved": self.convergence_achieved,
        }


class AntColonyOptimization:
    """
    Ant Colony Optimization algorithm implementation.

    This class implements the classic ACO algorithm with extensions for:
    - Multi-objective optimization
    - Spatial constraint handling
    - Dynamic environment adaptation
    - Integration with pheromone systems
    - Multiple ACO variants

    The algorithm simulates ant foraging behavior where artificial ants
    deposit pheromone trails on paths, and other ants follow these trails
    with probability proportional to pheromone concentration, leading to
    the discovery of optimal solutions.
    """

    def __init__(
        self,
        number_of_ants: int = 50,
        pheromone_evaporation_rate: float = 0.1,
        pheromone_deposition_amount: float = 1.0,
        alpha: float = 1.0,
        beta: float = 2.0,
        initial_pheromone: float = 1.0,
        max_iterations: int = 100,
        variant: str = "AS",  # 'AS', 'ACS', 'MMAS'
        spatial_graph: Optional[Any] = None,
        convergence_threshold: float = 0.001,
        **kwargs,
    ):
        """
        Initialize ACO algorithm.

        Args:
            number_of_ants: Number of artificial ants in the colony
            pheromone_evaporation_rate: Rate of pheromone evaporation per iteration
            pheromone_deposition_amount: Amount of pheromone deposited by ants
            alpha: Influence of pheromone trails
            beta: Influence of heuristic information
            initial_pheromone: Initial pheromone level on all edges
            max_iterations: Maximum number of optimization iterations
            variant: ACO variant ('AS', 'ACS', 'MMAS')
            spatial_graph: Spatial graph for path optimization
            **kwargs: Additional parameters
        """
        self.parameters = ACOParameters(
            number_of_ants=number_of_ants,
            pheromone_evaporation_rate=pheromone_evaporation_rate,
            pheromone_deposition_amount=pheromone_deposition_amount,
            alpha=alpha,
            beta=beta,
            initial_pheromone=initial_pheromone,
            max_iterations=max_iterations,
            convergence_threshold=convergence_threshold,
        )

        self.variant = variant
        self.spatial_graph = spatial_graph

        # Algorithm state
        self.pheromone_matrix: Dict[Tuple[Any, Any], float] = {}
        self.heuristic_matrix: Dict[Tuple[Any, Any], float] = {}
        self.problem_size: int = 0
        self.nodes: List[Any] = []

        # Optimization state
        self.best_solution: Optional[List[Any]] = None
        self.best_fitness: float = float("inf")
        self.global_best_solution: Optional[List[Any]] = None
        self.global_best_fitness: float = float("inf")

        # History tracking
        self.convergence_history: List[float] = []
        self.pheromone_history: List[Dict[str, float]] = []

        # Integration components
        self.spatial_indexer = None
        self.spatial_analytics = None
        self.pheromone_system = None

        # Performance tracking
        self.iteration_times: List[float] = []
        self.function_evaluations: int = 0

        # Initialize integrations
        self._initialize_integrations()

        logger.info(f"ACO initialized with {number_of_ants} ants, variant: {variant}")

    def _initialize_integrations(self) -> None:
        """Initialize integration with other GEO-INFER modules."""
        # Initialize spatial components
        if SpatialIndexingInterface:
            try:
                self.spatial_indexer = SpatialIndexingInterface(backend="h3")
                logger.info("Spatial indexer initialized for ACO")
            except Exception as e:
                logger.warning(f"Failed to initialize spatial indexer: {e}")

        if SpatialAnalyticsInterface:
            try:
                self.spatial_analytics = SpatialAnalyticsInterface(backend="h3")
                logger.info("Spatial analytics initialized for ACO")
            except Exception as e:
                logger.warning(f"Failed to initialize spatial analytics: {e}")

        # Initialize pheromone system
        try:
            from geo_infer_ant.core.stigmergy import PheromoneSystem

            self.pheromone_system = PheromoneSystem(
                spatial_resolution="h3_r8",
                pheromone_types=["trail", "food"],
                bounds={"min_lat": -90, "max_lat": 90, "min_lng": -180, "max_lng": 180},
            )
            logger.info("Pheromone system initialized for ACO")
        except Exception as e:
            logger.warning(f"Failed to initialize pheromone system: {e}")

    def initialize_problem(
        self,
        nodes: List[Any],
        distance_matrix: Optional[np.ndarray] = None,
        heuristic_matrix: Optional[np.ndarray] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the optimization problem.

        Args:
            nodes: List of nodes in the problem graph
            distance_matrix: Matrix of distances between nodes
            heuristic_matrix: Matrix of heuristic values (if different from distances)
            constraints: Problem constraints
        """
        self.nodes = nodes
        self.problem_size = len(nodes)
        self.constraints = constraints or {}

        # Initialize pheromone matrix
        self.pheromone_matrix = {}
        for i in range(self.problem_size):
            for j in range(self.problem_size):
                if i != j:
                    self.pheromone_matrix[(i, j)] = self.parameters.initial_pheromone

        # Initialize heuristic matrix (inverse of distance for TSP-like problems)
        self.heuristic_matrix = {}
        if heuristic_matrix is not None:
            # Use provided heuristic matrix
            for i in range(self.problem_size):
                for j in range(self.problem_size):
                    if i != j:
                        self.heuristic_matrix[(i, j)] = heuristic_matrix[i, j]
        elif distance_matrix is not None:
            # Use inverse distance as heuristic
            for i in range(self.problem_size):
                for j in range(self.problem_size):
                    if i != j:
                        if distance_matrix[i, j] > 0:
                            self.heuristic_matrix[(i, j)] = 1.0 / distance_matrix[i, j]
                        else:
                            self.heuristic_matrix[(i, j)] = 0.0
        else:
            # Default heuristic (random)
            for i in range(self.problem_size):
                for j in range(self.problem_size):
                    if i != j:
                        self.heuristic_matrix[(i, j)] = np.random.uniform(0.1, 1.0)

        logger.info(f"ACO problem initialized with {self.problem_size} nodes")

    def optimize_paths(
        self,
        start_locations: List[np.ndarray],
        end_locations: List[np.ndarray],
        objective_function: str = "minimize_total_distance",
        constraints: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Optimize paths between multiple start and end locations.

        Args:
            start_locations: Starting locations for path optimization
            end_locations: Destination locations
            objective_function: Objective to optimize
            constraints: Path constraints

        Returns:
            List of optimized paths with metadata
        """
        logger.info(
            f"Optimizing {len(start_locations)} paths from start to end locations"
        )

        optimized_paths = []

        for start, end in zip(start_locations, end_locations):
            # Create temporary problem for this path pair
            path_nodes = [start, end]

            # Add intermediate nodes if spatial graph available
            if self.spatial_graph:
                try:
                    # Find intermediate nodes between start and end
                    intermediate_nodes = self._find_intermediate_nodes(start, end)
                    path_nodes.extend(intermediate_nodes)
                except Exception as e:
                    logger.warning(f"Failed to find intermediate nodes: {e}")

            # Initialize problem for this path
            self.initialize_problem(path_nodes, constraints=constraints)

            # Run optimization
            result = self.solve()

            # Extract path information
            if result.best_solution:
                path_info = {
                    "start_location": start,
                    "end_location": end,
                    "optimal_path": [path_nodes[i] for i in result.best_solution],
                    "path_fitness": result.best_fitness,
                    "path_length": self._calculate_path_length(
                        result.best_solution, path_nodes
                    ),
                    "optimization_metadata": result.to_dict(),
                }
                optimized_paths.append(path_info)

        logger.info(
            f"Path optimization completed: {len(optimized_paths)} paths optimized"
        )
        return optimized_paths

    def _find_intermediate_nodes(
        self, start: np.ndarray, end: np.ndarray
    ) -> List[np.ndarray]:
        """Find intermediate nodes between start and end locations."""
        if not self.spatial_analytics:
            return []

        try:
            # Use spatial analytics to find intermediate points
            # This would integrate with actual spatial graph data
            return []
        except Exception as e:
            logger.warning(f"Failed to find intermediate nodes: {e}")
            return []

    def _calculate_path_length(
        self, path_indices: List[int], nodes: List[np.ndarray]
    ) -> float:
        """Calculate total length of a path."""
        if len(path_indices) < 2:
            return 0.0

        total_length = 0.0
        for i in range(len(path_indices) - 1):
            node1 = nodes[path_indices[i]]
            node2 = nodes[path_indices[i + 1]]
            total_length += np.linalg.norm(node2 - node1)

        return total_length

    def solve(self) -> OptimizationResult:
        """
        Solve the optimization problem using ACO.

        Returns:
            Optimization result with best solution and metadata
        """
        start_time = datetime.now()

        logger.info(
            f"Starting ACO optimization with {self.parameters.max_iterations} max iterations"
        )

        # Initialize algorithm state
        self._initialize_algorithm_state()

        # Main optimization loop
        for iteration in range(self.parameters.max_iterations):
            iteration_start = datetime.now()

            # Construct solutions using ants
            solutions = self._construct_solutions()

            # Update pheromone trails
            self._update_pheromones(solutions)

            # Update best solution
            self._update_best_solution(solutions)

            # Check convergence
            if self._check_convergence(iteration):
                logger.info(f"Convergence achieved at iteration {iteration}")
                break

            # Record iteration statistics
            self._record_iteration_stats(iteration)

            iteration_time = (datetime.now() - iteration_start).total_seconds()
            self.iteration_times.append(iteration_time)

        # Finalize results
        computation_time = (datetime.now() - start_time).total_seconds()

        result = OptimizationResult(
            best_solution=self.best_solution or [],
            best_fitness=self.best_fitness,
            convergence_history=self.convergence_history.copy(),
            pheromone_history=self.pheromone_history.copy(),
            computation_time=computation_time,
            iterations_completed=len(self.convergence_history),
            convergence_achieved=self._check_convergence(
                self.parameters.max_iterations - 1
            ),
        )

        logger.info(f"ACO optimization completed: best fitness = {result.best_fitness}")
        return result

    def _initialize_algorithm_state(self) -> None:
        """Initialize algorithm state for optimization."""
        self.best_solution = None
        self.best_fitness = float("inf")
        self.convergence_history = []
        self.pheromone_history = []
        self.iteration_times = []

        # Record initial state
        self._record_iteration_stats(0)

    def _construct_solutions(self) -> List[Dict[str, Any]]:
        """Construct solutions using artificial ants."""
        solutions = []

        for ant in range(self.parameters.number_of_ants):
            # Each ant constructs a solution
            solution = self._construct_single_solution(ant)
            fitness = self._evaluate_solution(solution)

            solutions.append({"solution": solution, "fitness": fitness, "ant_id": ant})

            self.function_evaluations += 1

        return solutions

    def _construct_single_solution(self, ant_id: int) -> List[int]:
        """Construct a single solution using one ant."""
        solution = []
        visited = set()

        # Start from random node (or node 0 for TSP-like problems)
        current_node = 0
        solution.append(current_node)
        visited.add(current_node)

        # Construct path until all nodes visited (TSP) or goal reached
        while len(solution) < self.problem_size:
            # Select next node using pheromone and heuristic information
            next_node = self._select_next_node(current_node, visited, ant_id)

            if next_node is None:
                break  # No valid next node

            solution.append(next_node)
            visited.add(next_node)
            current_node = next_node

        return solution

    def _select_next_node(
        self, current_node: int, visited: set, ant_id: int
    ) -> Optional[int]:
        """Select next node for ant based on pheromone and heuristic information."""
        candidates = []

        for node in range(self.problem_size):
            if node not in visited and node != current_node:
                # Calculate selection probability
                pheromone = self.pheromone_matrix.get(
                    (current_node, node), self.parameters.initial_pheromone
                )
                heuristic = self.heuristic_matrix.get((current_node, node), 0.0)

                # Apply power transformation
                pheromone_factor = pheromone**self.parameters.alpha
                heuristic_factor = heuristic**self.parameters.beta

                probability = pheromone_factor * heuristic_factor
                candidates.append((node, probability))

        if not candidates:
            return None

        # Select node using roulette wheel selection
        total_probability = sum(prob for _, prob in candidates)
        if total_probability <= 0:
            # Random selection if all probabilities are zero
            return np.random.choice([node for node, _ in candidates])

        # Normalize probabilities
        probabilities = [prob / total_probability for _, prob in candidates]

        # Select node
        selected_idx = np.random.choice(len(candidates), p=probabilities)
        return candidates[selected_idx][0]

    def _evaluate_solution(self, solution: List[int]) -> float:
        """Evaluate fitness of a solution."""
        if not solution or len(solution) < 2:
            return float("inf")

        # Calculate total path length (for TSP-like problems)
        total_distance = 0.0

        for i in range(len(solution) - 1):
            node1 = solution[i]
            node2 = solution[i + 1]

            # Get distance between nodes
            if hasattr(self, "distance_matrix") and self.distance_matrix is not None:
                distance = self.distance_matrix[node1, node2]
            else:
                # Calculate Euclidean distance if positions available
                if len(self.nodes) > max(node1, node2):
                    pos1 = np.array(self.nodes[node1])
                    pos2 = np.array(self.nodes[node2])
                    distance = np.linalg.norm(pos2 - pos1)
                else:
                    distance = 1.0  # Default distance

            total_distance += distance

        # Apply constraints penalties
        penalty = self._calculate_constraint_penalty(solution)
        fitness = total_distance + penalty

        return fitness

    def _calculate_constraint_penalty(self, solution: List[int]) -> float:
        """Calculate penalty for constraint violations."""
        penalty = 0.0

        # Example constraint: maximum path length
        if "max_path_length" in self.constraints:
            max_length = self.constraints["max_path_length"]
            actual_length = self._calculate_path_length(solution, self.nodes)

            if actual_length > max_length:
                penalty += (actual_length - max_length) * 10  # Penalty factor

        # Example constraint: required nodes
        if "required_nodes" in self.constraints:
            required = set(self.constraints["required_nodes"])
            solution_set = set(solution)

            missing_nodes = required - solution_set
            penalty += len(missing_nodes) * 100  # Large penalty for missing nodes

        return penalty

    def _update_pheromones(self, solutions: List[Dict[str, Any]]) -> None:
        """Update pheromone trails based on solution quality."""
        # Evaporate pheromones
        for edge, pheromone in self.pheromone_matrix.items():
            self.pheromone_matrix[edge] *= (
                1 - self.parameters.pheromone_evaporation_rate
            )

        # Apply variant-specific updates
        if self.variant == "ACS":
            self._update_pheromones_acs(solutions)
        elif self.variant == "MMAS":
            self._update_pheromones_mmas(solutions)
        else:  # AS (Ant System) - default
            self._update_pheromones_as(solutions)

        # Record pheromone statistics
        self._record_pheromone_stats()

    def _update_pheromones_as(self, solutions: List[Dict[str, Any]]) -> None:
        """Update pheromones using Ant System (AS) variant."""
        # Deposit pheromones based on solution quality
        for solution_info in solutions:
            solution = solution_info["solution"]
            fitness = solution_info["fitness"]

            # Calculate pheromone deposit amount (inverse of fitness)
            if fitness > 0:
                pheromone_amount = self.parameters.pheromone_deposition_amount / fitness
            else:
                pheromone_amount = self.parameters.pheromone_deposition_amount

            # Deposit on solution edges
            for i in range(len(solution) - 1):
                edge = (solution[i], solution[i + 1])
                self.pheromone_matrix[edge] += pheromone_amount

    def _update_pheromones_acs(self, solutions: List[Dict[str, Any]]) -> None:
        """Update pheromones using Ant Colony System (ACS) variant."""
        # Deposit pheromones only on best solution edges
        best_solution_info = min(solutions, key=lambda x: x["fitness"])
        best_solution = best_solution_info["solution"]
        best_fitness = best_solution_info["fitness"]

        if best_fitness > 0:
            pheromone_amount = (
                self.parameters.pheromone_deposition_amount / best_fitness
            )
        else:
            pheromone_amount = self.parameters.pheromone_deposition_amount

        # Deposit on best solution edges
        for i in range(len(best_solution) - 1):
            edge = (best_solution[i], best_solution[i + 1])
            self.pheromone_matrix[edge] += pheromone_amount

        # Also update global best if this is better
        if best_fitness < self.global_best_fitness:
            self.global_best_solution = best_solution.copy()
            self.global_best_fitness = best_fitness

            # Deposit additional pheromone on global best
            for i in range(len(self.global_best_solution) - 1):
                edge = (self.global_best_solution[i], self.global_best_solution[i + 1])
                self.pheromone_matrix[edge] += pheromone_amount

    def _update_pheromones_mmas(self, solutions: List[Dict[str, Any]]) -> None:
        """Update pheromones using Max-Min Ant System (MMAS) variant."""
        # Find best and worst solutions
        best_solution_info = min(solutions, key=lambda x: x["fitness"])
        worst_solution_info = max(solutions, key=lambda x: x["fitness"])

        best_fitness = best_solution_info["fitness"]
        _worst_fitness = worst_solution_info["fitness"]

        # Deposit pheromones only on best solution
        if best_fitness > 0:
            pheromone_amount = (
                self.parameters.pheromone_deposition_amount / best_fitness
            )
        else:
            pheromone_amount = self.parameters.pheromone_deposition_amount

        # Update best solution
        best_solution = best_solution_info["solution"]
        for i in range(len(best_solution) - 1):
            edge = (best_solution[i], best_solution[i + 1])
            self.pheromone_matrix[edge] += pheromone_amount

        # Enforce pheromone bounds
        for edge in self.pheromone_matrix:
            self.pheromone_matrix[edge] = max(
                self.parameters.min_pheromone,
                min(self.pheromone_matrix[edge], self.parameters.max_pheromone),
            )

    def _update_best_solution(self, solutions: List[Dict[str, Any]]) -> None:
        """Update best solution found so far."""
        # Find best solution in current iteration
        best_solution_info = min(solutions, key=lambda x: x["fitness"])
        current_best_fitness = best_solution_info["fitness"]

        # Update iteration best
        if current_best_fitness < self.best_fitness:
            self.best_solution = best_solution_info["solution"].copy()
            self.best_fitness = current_best_fitness

        # Update global best if this is better
        if current_best_fitness < self.global_best_fitness:
            self.global_best_solution = best_solution_info["solution"].copy()
            self.global_best_fitness = current_best_fitness

    def _check_convergence(self, iteration: int) -> bool:
        """Check if algorithm has converged."""
        if len(self.convergence_history) < 10:
            return False

        # Check if per-step improvement rate has dropped below threshold
        recent_fitness = self.convergence_history[-10:]
        if not np.all(np.isfinite(recent_fitness)):
            return False
        total_improvement = recent_fitness[0] - recent_fitness[-1]
        reference = max(abs(recent_fitness[0]), 1e-10)
        per_step_improvement = total_improvement / reference / len(recent_fitness)
        return bool(per_step_improvement < self.parameters.convergence_threshold)

    def _record_iteration_stats(self, iteration: int) -> None:
        """Record statistics for current iteration."""
        self.convergence_history.append(self.best_fitness)

        # Record pheromone statistics
        if self.pheromone_matrix:
            concentrations = list(self.pheromone_matrix.values())
            pheromone_stats = {
                "iteration": iteration,
                "max_pheromone": np.max(concentrations),
                "min_pheromone": np.min(concentrations),
                "avg_pheromone": np.mean(concentrations),
                "pheromone_std": np.std(concentrations),
            }
            self.pheromone_history.append(pheromone_stats)

    def _record_pheromone_stats(self) -> None:
        """Record current pheromone statistics."""
        if self.pheromone_matrix:
            concentrations = list(self.pheromone_matrix.values())
            stats = {
                "max_pheromone": np.max(concentrations),
                "min_pheromone": np.min(concentrations),
                "avg_pheromone": np.mean(concentrations),
            }
            self.pheromone_history.append(stats)

    def multi_objective_optimization(
        self,
        objectives: List[str],
        population_size: int = 100,
        generations: int = 50,
        spatial_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform multi-objective optimization using ACO.

        Args:
            objectives: List of objectives to optimize
            population_size: Size of solution population
            generations: Number of generations
            spatial_constraints: Spatial constraints for optimization

        Returns:
            Pareto front and optimization results
        """
        logger.info(f"Starting multi-objective ACO with objectives: {objectives}")

        if not objectives:
            raise ValueError("At least one objective must be specified")

        # Weighted-sum scalarisation over multiple objectives.
        # Each solution is evaluated independently per objective, then combined
        # via normalised weights.  Pareto efficiency is assessed post-hoc.
        n_objectives = len(objectives)
        weights = [1.0 / n_objectives] * n_objectives  # Uniform weights by default

        # Re-initialise with larger population
        original_ants = self.parameters.number_of_ants
        self.parameters.number_of_ants = max(original_ants, population_size)

        pareto_solutions: list = []

        for gen in range(generations):
            # Construct ant solutions
            solutions = self._construct_solutions()

            # Multi-objective fitness: weighted sum of normalised per-objective fitnesses
            obj_values_per_solution: list = []
            for sol_info in solutions:
                sol = sol_info["solution"]
                obj_vals = []
                for obj_name in objectives:
                    if obj_name == "minimize_total_distance":
                        obj_vals.append(self._evaluate_solution(sol))
                    elif obj_name == "maximize_pheromone_coverage":
                        covered = {(sol[i], sol[i + 1]) for i in range(len(sol) - 1)}
                        max_edges = max(1, self.problem_size * (self.problem_size - 1))
                        obj_vals.append(-len(covered) / max_edges)  # negate to minimise
                    else:
                        # Unknown objective: penalise path length as fallback
                        obj_vals.append(self._evaluate_solution(sol))
                obj_values_per_solution.append(obj_vals)

            # Normalise objectives across solutions in this generation
            obj_array = np.nan_to_num(
                np.array(obj_values_per_solution, dtype=float),
                nan=1e12,
                posinf=1e12,
                neginf=-1e12,
            )
            obj_min = obj_array.min(axis=0)
            obj_max = obj_array.max(axis=0)
            raw_range = obj_max - obj_min
            obj_range = np.where(raw_range > 0, raw_range, 1.0)
            obj_norm = (obj_array - obj_min) / obj_range

            for idx, sol_info in enumerate(solutions):
                scalar_fitness = float(np.dot(weights, obj_norm[idx]))
                pareto_solutions.append(
                    {
                        "solution": sol_info["solution"],
                        "objectives": dict(zip(objectives, obj_array[idx].tolist())),
                        "scalar_fitness": scalar_fitness,
                    }
                )

            # Pareto dominance filter (keep non-dominated solutions)
            if len(pareto_solutions) > population_size * 2:
                pareto_solutions = self._non_dominated_sort(
                    pareto_solutions, objectives
                )

            # Update pheromones using best scalar solution of current gen
            if solutions:
                best_scalar = min(
                    range(len(solutions)),
                    key=lambda i: float(np.dot(weights, obj_norm[i])),
                )
                self._update_pheromones([solutions[best_scalar]])

            # Apply spatial constraints by penalising solutions that violate them
            if spatial_constraints:
                for ps in pareto_solutions:
                    penalty = self._calculate_constraint_penalty(ps["solution"])
                    ps["scalar_fitness"] += penalty

        # Restore original number of ants
        self.parameters.number_of_ants = original_ants

        # Final non-dominated sort
        pareto_front_solutions = self._non_dominated_sort(pareto_solutions, objectives)

        pareto_front = {
            "solutions": pareto_front_solutions[:population_size],
            "objectives": objectives,
            "constraints": spatial_constraints,
            "metadata": {
                "algorithm": "Multi-Objective ACO (weighted-sum + Pareto)",
                "population_size": population_size,
                "generations": generations,
                "n_objectives": n_objectives,
                "weights": weights,
            },
        }

        logger.info(
            f"Multi-objective optimisation completed: {len(pareto_front_solutions)} Pareto solutions"
        )
        return pareto_front

    def adapt_to_changes(
        self,
        environmental_changes: Dict[str, Any],
        pheromone_update_strategy: str = "reinforcement_learning",
        convergence_monitoring: bool = True,
    ) -> Dict[str, Any]:
        """
        Adapt ACO algorithm to environmental changes.

        Args:
            environmental_changes: Description of environmental changes
            pheromone_update_strategy: Strategy for updating pheromones
            convergence_monitoring: Whether to monitor convergence

        Returns:
            Adaptation results and updated parameters
        """
        logger.info(f"Adapting ACO to environmental changes: {environmental_changes}")

        adaptation_results = {
            "changes_applied": [],
            "parameters_updated": {},
            "convergence_reset": False,
        }

        # Update pheromone evaporation based on environmental volatility
        if "volatility" in environmental_changes:
            volatility = environmental_changes["volatility"]

            # Increase evaporation rate in volatile environments
            old_rate = self.parameters.pheromone_evaporation_rate
            new_rate = min(0.5, old_rate * (1 + volatility))

            self.parameters.pheromone_evaporation_rate = new_rate
            adaptation_results["parameters_updated"][
                "pheromone_evaporation_rate"
            ] = new_rate
            adaptation_results["changes_applied"].append(
                "pheromone_evaporation_adjusted"
            )

        # Update exploration rate based on problem complexity
        if "problem_complexity" in environmental_changes:
            complexity = environmental_changes["problem_complexity"]

            old_exploration = getattr(self.parameters, "exploration_rate", 0.1)
            new_exploration = min(0.3, old_exploration * (1 + complexity * 0.5))

            self.parameters.exploration_rate = new_exploration
            adaptation_results["parameters_updated"][
                "exploration_rate"
            ] = new_exploration
            adaptation_results["changes_applied"].append("exploration_rate_adjusted")

        # Reset convergence tracking if major changes
        if environmental_changes.get("major_change", False):
            self.convergence_history = []
            adaptation_results["convergence_reset"] = True
            adaptation_results["changes_applied"].append("convergence_reset")

        logger.info(
            f"ACO adaptation completed: {len(adaptation_results['changes_applied'])} changes applied"
        )
        return adaptation_results

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics."""
        stats = {
            "algorithm": "Ant Colony Optimization",
            "variant": self.variant,
            "parameters": {
                "number_of_ants": self.parameters.number_of_ants,
                "pheromone_evaporation_rate": self.parameters.pheromone_evaporation_rate,
                "alpha": self.parameters.alpha,
                "beta": self.parameters.beta,
                "max_iterations": self.parameters.max_iterations,
            },
            "problem_info": {
                "problem_size": self.problem_size,
                "number_of_nodes": len(self.nodes),
                "constraints": self.constraints,
            },
            "optimization_results": {
                "best_fitness": self.best_fitness,
                "global_best_fitness": self.global_best_fitness,
                "iterations_completed": len(self.convergence_history),
                "function_evaluations": self.function_evaluations,
            },
            "pheromone_statistics": {},
        }

        # Pheromone statistics
        if self.pheromone_matrix:
            concentrations = list(self.pheromone_matrix.values())
            stats["pheromone_statistics"] = {
                "max_pheromone": np.max(concentrations),
                "min_pheromone": np.min(concentrations),
                "avg_pheromone": np.mean(concentrations),
                "std_pheromone": np.std(concentrations),
                "active_edges": len(
                    [c for c in concentrations if c > self.parameters.min_pheromone]
                ),
            }

        # Performance statistics
        if self.iteration_times:
            stats["performance"] = {
                "avg_iteration_time": np.mean(self.iteration_times),
                "total_computation_time": sum(self.iteration_times),
                "iterations_per_second": len(self.iteration_times)
                / sum(self.iteration_times),
            }

        return stats

    def _non_dominated_sort(self, solutions: list, objectives: list) -> list:
        """Return non-dominated (Pareto front) solutions.

        Uses a pairwise dominance check:  solution A dominates solution B if
        A is not worse on any objective and strictly better on at least one.
        Complexity: O(n^2 * |objectives|) — acceptable for typical MOACO sizes.
        """
        n = len(solutions)
        dominated = [False] * n

        for i in range(n):
            if dominated[i]:
                continue
            for j in range(n):
                if i == j or dominated[j]:
                    continue
                # Check if solution i dominates solution j
                obj_i = [solutions[i]["objectives"].get(o, 0.0) for o in objectives]
                obj_j = [solutions[j]["objectives"].get(o, 0.0) for o in objectives]
                # i dominates j: not worse in all, strictly better in at least one
                not_worse = all(vi <= vj for vi, vj in zip(obj_i, obj_j))
                strictly_better = any(vi < vj for vi, vj in zip(obj_i, obj_j))
                if not_worse and strictly_better:
                    dominated[j] = True

        return [s for s, dom in zip(solutions, dominated) if not dom]

    def save_optimization_state(self, filepath: str) -> bool:
        """Save optimization state to file."""
        try:
            import json

            state = {
                "variant": self.variant,
                "parameters": {
                    "number_of_ants": self.parameters.number_of_ants,
                    "pheromone_evaporation_rate": self.parameters.pheromone_evaporation_rate,
                    "pheromone_deposition_amount": self.parameters.pheromone_deposition_amount,
                    "alpha": self.parameters.alpha,
                    "beta": self.parameters.beta,
                    "initial_pheromone": self.parameters.initial_pheromone,
                    "max_iterations": self.parameters.max_iterations,
                },
                "problem_state": {
                    "nodes": self.nodes,
                    "problem_size": self.problem_size,
                    "constraints": self.constraints,
                },
                "pheromone_matrix": {
                    str(edge): pheromone
                    for edge, pheromone in self.pheromone_matrix.items()
                },
                "heuristic_matrix": {
                    str(edge): heuristic
                    for edge, heuristic in self.heuristic_matrix.items()
                },
                "optimization_results": {
                    "best_solution": self.best_solution,
                    "best_fitness": self.best_fitness,
                    "global_best_solution": self.global_best_solution,
                    "global_best_fitness": self.global_best_fitness,
                },
                "history": {
                    "convergence_history": self.convergence_history,
                    "pheromone_history": self.pheromone_history,
                    "iteration_times": self.iteration_times,
                },
            }

            with open(filepath, "w") as f:
                json.dump(state, f, indent=2)

            logger.info(f"ACO state saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save ACO state: {e}")
            return False

    def load_optimization_state(self, filepath: str) -> bool:
        """Load optimization state from file."""
        try:
            import json

            with open(filepath, "r") as f:
                state = json.load(f)

            # Restore variant (stored at top level, not inside parameters)
            self.variant = state.get("variant", "AS")

            # Restore parameters
            params = state["parameters"]
            self.parameters = ACOParameters(**params)

            # Restore problem state
            problem = state["problem_state"]
            self.nodes = problem["nodes"]
            self.problem_size = problem["problem_size"]
            self.constraints = problem["constraints"]

            # Restore pheromone and heuristic matrices
            self.pheromone_matrix = {
                tuple(eval(edge)): pheromone
                for edge, pheromone in state["pheromone_matrix"].items()
            }
            self.heuristic_matrix = {
                tuple(eval(edge)): heuristic
                for edge, heuristic in state["heuristic_matrix"].items()
            }

            # Restore optimization results
            results = state["optimization_results"]
            self.best_solution = results["best_solution"]
            self.best_fitness = results["best_fitness"]
            self.global_best_solution = results["global_best_solution"]
            self.global_best_fitness = results["global_best_fitness"]

            # Restore history
            history = state["history"]
            self.convergence_history = history["convergence_history"]
            self.pheromone_history = history["pheromone_history"]
            self.iteration_times = history["iteration_times"]

            logger.info(f"ACO state loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load ACO state: {e}")
            return False
