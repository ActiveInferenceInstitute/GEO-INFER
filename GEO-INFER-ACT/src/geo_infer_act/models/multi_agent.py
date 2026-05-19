"""
Multi-agent model for active inference.
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np
import logging

from geo_infer_act.models.base import ActiveInferenceModel, CategoricalModel
from geo_infer_act.utils.h3_adapter import get_h3_adapter, normalize_belief_vector

logger = logging.getLogger(__name__)


class MultiAgentModel(ActiveInferenceModel):
    """Multi-agent coordination using active inference and stigmergy."""

    def __init__(
        self,
        n_agents: int = 3,
        n_resources: int = 4,
        n_locations: int = 5,
        planning_horizon: int = 10,
        config: Optional[Dict[str, Any]] = None,
        environmental_engine: Optional[Any] = None,
    ):
        super().__init__(config)
        self.n_agents = n_agents
        self.n_resources = n_resources
        self.n_locations = n_locations
        self.planning_horizon = planning_horizon
        self.environmental_engine = environmental_engine

        # Initialize agent models with enhanced active inference capabilities
        self.agent_models = []
        for i in range(self.n_agents):
            agent = CategoricalModel(
                state_dim=4, obs_dim=4
            )  # 4-state environmental model
            # Set up proper observation and transition models
            agent.set_likelihood_matrix(self._create_environmental_observation_model())
            agent.set_transition_matrix(self._create_environmental_transition_model())
            self.agent_models.append(agent)

        self.resource_distribution = np.random.rand(self.n_resources, self.n_locations)
        self.location_connectivity = np.eye(
            self.n_locations
        )  # Example, adjust as needed
        self.agent_preferences = np.random.rand(self.n_agents, self.n_resources)

        # H3 spatial properties
        self.spatial_mode = False
        self.h3_cells = []
        self.h3_resolution = 8
        self.spatial_graph = None
        self.agent_location_map = {}

    def _create_environmental_observation_model(self) -> np.ndarray:
        """Create realistic environmental observation model for agents."""
        # Observation model: P(observation | environmental_state)
        # States: [poor, fair, good, excellent] environmental quality
        # Observations: [low_temp, med_temp, high_temp, vegetation] indicators

        obs_model = np.array(
            [
                [0.7, 0.5, 0.3, 0.1],  # Low temperature observation
                [0.2, 0.3, 0.4, 0.3],  # Medium temperature observation
                [0.1, 0.2, 0.3, 0.6],  # High temperature observation
                [0.1, 0.3, 0.6, 0.8],  # Vegetation density observation
            ]
        )

        # Normalize columns (each state sums to 1)
        obs_model = obs_model / obs_model.sum(axis=0, keepdims=True)
        return obs_model

    def _create_environmental_transition_model(self) -> np.ndarray:
        """Create environmental state transition model."""
        # Transition model: P(next_state | current_state)
        # Environmental states tend to persist with some probability of change

        transition_model = np.array(
            [
                [0.7, 0.2, 0.05, 0.05],  # From poor state
                [0.2, 0.6, 0.15, 0.05],  # From fair state
                [0.05, 0.15, 0.6, 0.2],  # From good state
                [0.05, 0.05, 0.2, 0.7],  # From excellent state
            ]
        )

        return transition_model

    def step(
        self, actions: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """Advance the multi-agent model and return observable state."""
        agent_locations = []
        for agent in self.agent_models:
            if hasattr(agent, "location"):
                agent_locations.append(agent.location)
            else:
                agent_locations.append(0)  # Default location
        return {
            "resource_distribution": self.resource_distribution.copy(),
            "agent_locations": agent_locations,
        }, False

    def enable_h3_spatial(self, resolution: int, boundary: Dict[str, Any]):
        """
        Enable H3 spatial modeling for multi-agent active inference.

        A real H3 v4 cell set is created from the supplied boundary, each cell
        receives a categorical active-inference agent, and a neighbor graph is
        built from H3 ring adjacency for distributed belief coordination.
        """
        from geo_infer_act.utils.integration import create_h3_spatial_model

        try:
            adapter = get_h3_adapter()
            result = create_h3_spatial_model({}, resolution, boundary)
            if result["status"] == "success":
                self.spatial_mode = True
                self.h3_resolution = resolution
                self.h3_cells = result["model_config"]["boundary_cells"]
                if not self.h3_cells:
                    raise ValueError("H3 spatial model did not produce any cells")
                self.h3_cells = adapter.validate_cells(self.h3_cells)
                self.n_locations = len(self.h3_cells)

                # Create one agent per H3 cell for distributed spatial inference
                self.agent_models = []
                for i, cell in enumerate(self.h3_cells):
                    agent = CategoricalModel(state_dim=4, obs_dim=4)
                    agent.cell_id = cell
                    agent.spatial_index = i

                    # Set up environmental models
                    agent.set_likelihood_matrix(
                        self._create_environmental_observation_model()
                    )
                    agent.set_transition_matrix(
                        self._create_environmental_transition_model()
                    )

                    # Initialize with spatial-dependent priors
                    try:
                        lat, lng = adapter.cell_to_latlng(cell)
                        if self.environmental_engine is not None and hasattr(
                            self.environmental_engine, "compute_spatial_priors"
                        ):
                            # Use true Moran's I weighted spatial priors from the environmental engine
                            try:
                                priors_map = (
                                    self.environmental_engine.compute_spatial_priors(
                                        "vegetation_density", 4
                                    )
                                )
                                initial_beliefs = priors_map.get(cell, np.ones(4) / 4)
                            except Exception as e:
                                logger.warning(f"Failed to fetch Moran prior: {e}")
                                initial_beliefs = np.ones(4) / 4
                        else:
                            # Create location-dependent initial beliefs from coordinates.
                            spatial_bias = np.array(
                                [0.1, 0.2, 0.4, 0.3]
                            )  # Slight bias toward good states
                            # Add some spatial variation based on coordinates
                            spatial_variation = (
                                0.1 * np.sin(lat * 10) * np.cos(lng * 10)
                            )
                            initial_beliefs = spatial_bias + spatial_variation
                            initial_beliefs = normalize_belief_vector(initial_beliefs)

                        agent.beliefs = initial_beliefs
                    except Exception as e:
                        logger.warning(
                            "Spatial belief initialization used uniform beliefs: %s",
                            e,
                        )
                        agent.beliefs = np.ones(4) / 4

                    self.agent_models.append(agent)

                # Create spatial coordination graph
                self._create_spatial_coordination_graph()

                logger.info(
                    f"Enabled H3 spatial mode with {self.n_locations} cells and {len(self.agent_models)} agents"
                )
            else:
                raise RuntimeError(
                    f"H3 spatial initialization failed: {result['message']}"
                )
        except Exception as e:
            logger.error(f"Failed to enable H3 spatial mode: {e}")
            raise

    def _create_spatial_coordination_graph(self):
        """Create coordination graph between spatially neighboring agents."""
        if not self.spatial_mode or not self.h3_cells:
            return

        adapter = get_h3_adapter()
        self.spatial_graph = {}

        for i, cell in enumerate(self.h3_cells):
            neighbors = []
            try:
                h3_neighbors = adapter.grid_ring(cell, 1)
                valid_neighbors = set(h3_neighbors) & set(self.h3_cells)

                for neighbor_cell in valid_neighbors:
                    if neighbor_cell in self.h3_cells:
                        neighbor_idx = self.h3_cells.index(neighbor_cell)
                        neighbors.append(neighbor_idx)

            except Exception as e:
                logger.debug("Failed to get H3 neighbors for cell %s: %s", cell, e)

            self.spatial_graph[i] = neighbors

    def simulate_h3_lattice(
        self, timesteps: int, obs_gen: Callable[[str], np.ndarray]
    ) -> List[Dict[str, Dict]]:
        """
        Simulate active inference on H3 lattice with proper perception-action loops.

        Each timestep generates one normalized observation vector per H3 cell,
        updates the corresponding agent beliefs, records finite free-energy
        diagnostics, and then performs neighbor-based belief coordination or
        environmental stigmergy when an environmental engine is attached.

        Args:
            timesteps: Number of simulation timesteps
            obs_gen: Function that generates observations for each H3 cell

        Returns:
            History of simulation states
        """
        if not self.spatial_mode:
            raise ValueError("Enable H3 spatial mode first")

        history = []

        for t in range(timesteps):
            step_data = {}

            # Perception phase: each agent updates beliefs based on observations
            for i, (cell, agent) in enumerate(zip(self.h3_cells, self.agent_models)):
                # Generate environmental observation for this cell
                obs = obs_gen(cell)

                # Ensure observation is properly formatted (4-dimensional for our model)
                if len(obs) != 4:
                    # Convert to 4D observation vector
                    obs_4d = np.zeros(4)
                    for j in range(min(len(obs), 4)):
                        obs_4d[j] = obs[j]
                    obs = obs_4d

                # Normalize observation to probability distribution
                obs = normalize_belief_vector(obs)

                # Update agent beliefs using Bayesian inference
                try:
                    updated_beliefs = agent.update_beliefs(obs)

                    # Compute free energy for this agent
                    free_energy = agent.compute_free_energy()

                    # Store agent state
                    step_data[cell] = {
                        "beliefs": updated_beliefs.tolist(),
                        "observations": obs.tolist(),
                        "free_energy": free_energy,
                        "agent_index": i,
                    }

                except Exception as e:
                    raise RuntimeError(
                        f"Failed to update beliefs for agent {i} at cell {cell}: {e}"
                    ) from e

            # Action/Coordination phase: agents coordinate and influence each other
            self._spatial_belief_coordination(step_data)

            history.append(step_data)

            if t % 5 == 0:
                logger.debug(f"H3 simulation timestep {t}/{timesteps} completed")

        logger.info(
            f"Completed H3 lattice simulation: {timesteps} timesteps, {len(self.h3_cells)} cells"
        )
        return history

    def _spatial_belief_coordination(self, step_data: Dict[str, Dict]):
        """Coordinate agents through environmental updates or spatial belief sharing."""
        if not self.spatial_graph:
            return

        # True Stigmergic Communication:
        # Agents modify the shared environmental manifold directly (stigmergy).
        if self.environmental_engine is not None:
            self._apply_stigmergy(step_data)
            # Beliefs will be naturally updated in the next perception cycle via `obs_gen`
            return

        coordination_strength = 0.1  # How much neighbors influence each other

        # Create a copy of current beliefs for simultaneous update
        updated_beliefs = {}

        for i, cell in enumerate(self.h3_cells):
            if cell not in step_data:
                continue

            current_beliefs = np.array(step_data[cell]["beliefs"])
            neighbor_indices = self.spatial_graph.get(i, [])

            if neighbor_indices:
                # Aggregate neighbor beliefs
                neighbor_beliefs = []
                for neighbor_idx in neighbor_indices:
                    if neighbor_idx < len(self.h3_cells):
                        neighbor_cell = self.h3_cells[neighbor_idx]
                        if neighbor_cell in step_data:
                            neighbor_beliefs.append(
                                np.array(step_data[neighbor_cell]["beliefs"])
                            )

                if neighbor_beliefs:
                    avg_neighbor_belief = np.mean(neighbor_beliefs, axis=0)

                    # Coordinate beliefs with neighbors
                    coordinated_beliefs = (
                        (1 - coordination_strength) * current_beliefs
                        + coordination_strength * avg_neighbor_belief
                    )
                    coordinated_beliefs = coordinated_beliefs / (
                        np.sum(coordinated_beliefs) + 1e-8
                    )

                    updated_beliefs[cell] = coordinated_beliefs
                else:
                    updated_beliefs[cell] = current_beliefs
            else:
                updated_beliefs[cell] = current_beliefs

        # Update step data with coordinated beliefs
        for cell, new_beliefs in updated_beliefs.items():
            if cell in step_data:
                step_data[cell]["beliefs"] = new_beliefs.tolist()

                # Update agent model beliefs for next timestep
                agent_idx = step_data[cell]["agent_index"]
                if agent_idx < len(self.agent_models):
                    self.agent_models[agent_idx].beliefs = new_beliefs

    def _apply_stigmergy(self, step_data: Dict[str, Dict]):
        """Apply stigmergic pheromone modification to the environmental engine."""
        stigmergy_strength = 0.05
        current_time = 0.0  # Could be synced with global time if needed

        observations_to_push = {}
        for cell, data in step_data.items():
            if cell in self.environmental_engine.environmental_states:
                # Based on the agent's beliefs (e.g. they believe it's a good state), they modify the environment
                # E.g. high belief in state index 3 (excellent)
                belief_tensor = np.array(data["beliefs"])
                positive_pull = belief_tensor[3] - belief_tensor[0]

                # We modify standard fields to reflect the presence/activity of agents
                # Example: human_activity increases, which can subsequently influence observations
                current_activity = getattr(
                    self.environmental_engine.environmental_states[cell],
                    "human_activity",
                    0.0,
                )
                new_activity = np.clip(
                    current_activity + (positive_pull * stigmergy_strength), 0.0, 1.0
                )

                observations_to_push[cell] = {"human_activity": new_activity}

        # Push all modifications back to the environmental engine as new observations
        if observations_to_push:
            self.environmental_engine.observe_environment(
                observations_to_push, timestamp=current_time
            )

    def coordinate_agents(self) -> Dict[str, Any]:
        """
        Coordinate agents through message passing and shared information.

        Returns:
            Coordination results including coherence metrics
        """
        if not hasattr(self, "spatial_mode") or not self.spatial_mode:
            # Simple coordination for non-spatial case
            coordination_matrix = np.random.rand(self.n_agents, self.n_agents)
            coordination_matrix = (
                coordination_matrix + coordination_matrix.T
            ) / 2  # Make symmetric
            np.fill_diagonal(coordination_matrix, 1.0)  # Perfect self-coordination

            return {
                "coordination_matrix": coordination_matrix,
                "average_coordination": np.mean(
                    coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]
                ),
                "coordination_variance": np.var(
                    coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]
                ),
            }

        # Spatial coordination using H3 cells
        n_cells = len(self.h3_cells)
        coordination_matrix = np.eye(n_cells)  # Start with identity

        # Add spatial coordination based on H3 neighbor relationships.
        adapter = get_h3_adapter()
        h3_cells = adapter.validate_cells(self.h3_cells)
        for i, cell_i in enumerate(h3_cells):
            neighbors = set(adapter.grid_ring(cell_i, 1))
            for j, cell_j in enumerate(h3_cells):
                if cell_j in neighbors and i != j:
                    agent_i = self.agent_models[i]
                    agent_j = self.agent_models[j]

                    if hasattr(agent_i, "beliefs") and hasattr(agent_j, "beliefs"):
                        belief_i = normalize_belief_vector(agent_i.beliefs)
                        belief_j = normalize_belief_vector(agent_j.beliefs)
                        belief_similarity = 1.0 / (
                            1.0 + np.linalg.norm(belief_i - belief_j)
                        )
                        coordination_matrix[i, j] = belief_similarity
                    else:
                        coordination_matrix[i, j] = 0.5

        return {
            "coordination_matrix": coordination_matrix,
            "average_coordination": np.mean(
                coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]
            ),
            "coordination_variance": np.var(
                coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]
            ),
            "n_coordinated_agents": n_cells,
        }

    def get_agent_messages(self, agent_id: int) -> Dict[str, Any]:
        """Get messages for inter-agent communication from the specified agent.

        Returns a snapshot of the agent's current beliefs, position, and
        recent interactions for use in multi-agent coordination protocols.

        Args:
            agent_id: Integer index of the agent

        Returns:
            Dict with 'beliefs', 'position', 'last_action', 'free_energy',
            and 'timestamp' keys. Empty dict if agent_id is invalid.
        """
        if agent_id < 0 or agent_id >= len(self.agent_models):
            logger.warning(
                f"Invalid agent_id {agent_id}, valid range [0, {len(self.agent_models)})"
            )
            return {}

        agent = self.agent_models[agent_id]
        message: Dict[str, Any] = {
            "agent_id": agent_id,
            "beliefs": (
                agent.beliefs.tolist()
                if hasattr(agent, "beliefs") and agent.beliefs is not None
                else []
            ),
        }

        # Include spatial position if H3 mode is active
        if (
            hasattr(self, "spatial_mode")
            and self.spatial_mode
            and agent_id < len(self.h3_cells)
        ):
            message["position"] = self.h3_cells[agent_id]

        # Include recent action info from history
        if hasattr(self, "history") and self.history:
            last_step = self.history[-1]
            if isinstance(last_step, dict):
                cell_key = (
                    self.h3_cells[agent_id]
                    if hasattr(self, "h3_cells") and agent_id < len(self.h3_cells)
                    else str(agent_id)
                )
                if cell_key in last_step:
                    cell_data = last_step[cell_key]
                    message["last_action"] = cell_data.get("action")
                    message["free_energy"] = cell_data.get("free_energy")

        return message
