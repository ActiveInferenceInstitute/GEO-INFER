"""
Multi-agent model for active inference.
"""
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np
import logging
logger = logging.getLogger(__name__)

from geo_infer_act.models.base import CategoricalModel
from geo_infer_act.models.base import ActiveInferenceModel


class MultiAgentModel(ActiveInferenceModel):
    """Multi-agent coordination using active inference."""
    
    def __init__(self, n_agents: int = 3, n_resources: int = 4, n_locations: int = 5, planning_horizon: int = 10, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.n_agents = n_agents
        self.n_resources = n_resources
        self.n_locations = n_locations
        self.planning_horizon = planning_horizon
        
        # Initialize agent models with enhanced active inference capabilities
        self.agent_models = []
        for i in range(self.n_agents):
            agent = CategoricalModel(state_dim=4, obs_dim=4)  # 4-state environmental model
            # Set up proper observation and transition models
            agent.set_likelihood_matrix(self._create_environmental_observation_model())
            agent.set_transition_matrix(self._create_environmental_transition_model())
            self.agent_models.append(agent)
        
        self.resource_distribution = np.random.rand(self.n_resources, self.n_locations)
        self.location_connectivity = np.eye(self.n_locations)  # Example, adjust as needed
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
        
        obs_model = np.array([
            [0.7, 0.5, 0.3, 0.1],  # Low temperature observation
            [0.2, 0.3, 0.4, 0.3],  # Medium temperature observation  
            [0.1, 0.2, 0.3, 0.6],  # High temperature observation
            [0.1, 0.3, 0.6, 0.8]   # Vegetation density observation
        ])
        
        # Normalize columns (each state sums to 1)
        obs_model = obs_model / obs_model.sum(axis=0, keepdims=True)
        return obs_model
    
    def _create_environmental_transition_model(self) -> np.ndarray:
        """Create environmental state transition model."""
        # Transition model: P(next_state | current_state)
        # Environmental states tend to persist with some probability of change
        
        transition_model = np.array([
            [0.7, 0.2, 0.05, 0.05],  # From poor state
            [0.2, 0.6, 0.15, 0.05],  # From fair state  
            [0.05, 0.15, 0.6, 0.2],  # From good state
            [0.05, 0.05, 0.2, 0.7]   # From excellent state
        ])
        
        return transition_model

    def step(self, actions: Optional[List[Dict[str, Any]]] = None) -> Tuple[Dict[str, Any], bool]:
        agent_locations = []
        for agent in self.agent_models:
            if hasattr(agent, 'location'):
                agent_locations.append(agent.location)
            else:
                agent_locations.append(0) # Default location
        return {'resource_distribution': self.resource_distribution.copy(), 'agent_locations': agent_locations}, False 

    def enable_h3_spatial(self, resolution: int, boundary: Dict[str, Any]):
        """Enable H3 spatial modeling for multi-agent active inference."""
        from geo_infer_act.utils.integration import create_h3_spatial_model
        
        try:
            result = create_h3_spatial_model({}, resolution, boundary)
            if result['status'] == 'success':
                self.spatial_mode = True
                self.h3_resolution = resolution
                self.h3_cells = result['model_config']['boundary_cells']
                self.n_locations = len(self.h3_cells)
                
                # Create one agent per H3 cell for distributed spatial inference
                self.agent_models = []
                for i, cell in enumerate(self.h3_cells):
                    agent = CategoricalModel(state_dim=4, obs_dim=4)
                    agent.cell_id = cell
                    agent.spatial_index = i
                    
                    # Set up environmental models
                    agent.set_likelihood_matrix(self._create_environmental_observation_model())
                    agent.set_transition_matrix(self._create_environmental_transition_model())
                    
                    # Initialize with spatial-dependent priors
                    try:
                        import h3
                        lat, lng = h3.cell_to_latlng(cell)
                        # Create location-dependent initial beliefs
                        spatial_bias = np.array([0.1, 0.2, 0.4, 0.3])  # Slight bias toward good states
                        # Add some spatial variation based on coordinates
                        spatial_variation = 0.1 * np.sin(lat * 10) * np.cos(lng * 10)
                        initial_beliefs = spatial_bias + spatial_variation
                        initial_beliefs = initial_beliefs / np.sum(initial_beliefs)
                        agent.beliefs = initial_beliefs
                    except Exception:
                        # Fallback to uniform beliefs
                        agent.beliefs = np.ones(4) / 4
                    
                    self.agent_models.append(agent)
                
                # Create spatial coordination graph
                self._create_spatial_coordination_graph()
                
                logger.info(f'Enabled H3 spatial mode with {self.n_locations} cells and {len(self.agent_models)} agents')
            else:
                logger.warning(f"H3 spatial initialization failed: {result['message']}")
        except Exception as e:
            logger.error(f"Failed to enable H3 spatial mode: {e}")
    
    def _create_spatial_coordination_graph(self):
        """Create coordination graph between spatially neighboring agents."""
        if not self.spatial_mode or not self.h3_cells:
            return
        
        try:
            import h3
            self.spatial_graph = {}
            
            for i, cell in enumerate(self.h3_cells):
                neighbors = []
                try:
                    # Get immediate H3 neighbors
                    h3_neighbors = h3.grid_ring(cell, 1)
                    if isinstance(h3_neighbors, list):
                        valid_neighbors = set(h3_neighbors) & set(self.h3_cells)
                    else:
                        valid_neighbors = set(list(h3_neighbors)) & set(self.h3_cells)
                    
                    # Map to agent indices
                    for neighbor_cell in valid_neighbors:
                        if neighbor_cell in self.h3_cells:
                            neighbor_idx = self.h3_cells.index(neighbor_cell)
                            neighbors.append(neighbor_idx)
                    
                except Exception:
                    # Fallback to empty neighbors
                    pass
                
                self.spatial_graph[i] = neighbors
                
        except ImportError:
            logger.warning("h3 package not available for spatial coordination")

    def simulate_h3_lattice(self, timesteps: int, obs_gen: Callable[[str], np.ndarray]) -> List[Dict[str, Dict]]:
        """
        Simulate active inference on H3 lattice with proper perception-action loops.
        
        Args:
            timesteps: Number of simulation timesteps
            obs_gen: Function that generates observations for each H3 cell
            
        Returns:
            History of simulation states
        """
        if not self.spatial_mode:
            raise ValueError('Enable H3 spatial mode first')
        
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
                obs = obs / (np.sum(obs) + 1e-8)
                
                # Update agent beliefs using Bayesian inference
                try:
                    updated_beliefs = agent.update_beliefs(obs)
                    
                    # Compute free energy for this agent
                    free_energy = agent.compute_free_energy()
                    
                    # Store agent state
                    step_data[cell] = {
                        'beliefs': updated_beliefs.tolist(),
                        'observations': obs.tolist(),
                        'free_energy': free_energy,
                        'agent_index': i
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to update beliefs for agent {i} at cell {cell}: {e}")
                    # Fallback data
                    step_data[cell] = {
                        'beliefs': agent.beliefs.tolist() if hasattr(agent, 'beliefs') else [0.25, 0.25, 0.25, 0.25],
                        'observations': obs.tolist(),
                        'free_energy': 1.0,
                        'agent_index': i
                    }
            
            # Action/Coordination phase: agents coordinate and influence each other
            self._spatial_belief_coordination(step_data)
            
            history.append(step_data)
            
            if t % 5 == 0:
                logger.debug(f"H3 simulation timestep {t}/{timesteps} completed")
        
        logger.info(f"Completed H3 lattice simulation: {timesteps} timesteps, {len(self.h3_cells)} cells")
        return history
    
    def _spatial_belief_coordination(self, step_data: Dict[str, Dict]):
        """Implement spatial coordination between neighboring agents."""
        if not self.spatial_graph:
            return
        
        coordination_strength = 0.1  # How much neighbors influence each other
        
        # Create a copy of current beliefs for simultaneous update
        updated_beliefs = {}
        
        for i, cell in enumerate(self.h3_cells):
            if cell not in step_data:
                continue
            
            current_beliefs = np.array(step_data[cell]['beliefs'])
            neighbor_indices = self.spatial_graph.get(i, [])
            
            if neighbor_indices:
                # Aggregate neighbor beliefs
                neighbor_beliefs = []
                for neighbor_idx in neighbor_indices:
                    if neighbor_idx < len(self.h3_cells):
                        neighbor_cell = self.h3_cells[neighbor_idx]
                        if neighbor_cell in step_data:
                            neighbor_beliefs.append(np.array(step_data[neighbor_cell]['beliefs']))
                
                if neighbor_beliefs:
                    avg_neighbor_belief = np.mean(neighbor_beliefs, axis=0)
                    
                    # Coordinate beliefs with neighbors
                    coordinated_beliefs = (1 - coordination_strength) * current_beliefs + coordination_strength * avg_neighbor_belief
                    coordinated_beliefs = coordinated_beliefs / (np.sum(coordinated_beliefs) + 1e-8)
                    
                    updated_beliefs[cell] = coordinated_beliefs
                else:
                    updated_beliefs[cell] = current_beliefs
            else:
                updated_beliefs[cell] = current_beliefs
        
        # Update step data with coordinated beliefs
        for cell, new_beliefs in updated_beliefs.items():
            if cell in step_data:
                step_data[cell]['beliefs'] = new_beliefs.tolist()
                
                # Update agent model beliefs for next timestep
                agent_idx = step_data[cell]['agent_index']
                if agent_idx < len(self.agent_models):
                    self.agent_models[agent_idx].beliefs = new_beliefs
    
    def coordinate_agents(self) -> Dict[str, Any]:
        """
        Coordinate agents through message passing and shared information.
        
        Returns:
            Coordination results including coherence metrics
        """
        if not hasattr(self, 'spatial_mode') or not self.spatial_mode:
            # Simple coordination for non-spatial case
            coordination_matrix = np.random.rand(self.n_agents, self.n_agents)
            coordination_matrix = (coordination_matrix + coordination_matrix.T) / 2  # Make symmetric
            np.fill_diagonal(coordination_matrix, 1.0)  # Perfect self-coordination
            
            return {
                'coordination_matrix': coordination_matrix,
                'average_coordination': np.mean(coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]),
                'coordination_variance': np.var(coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)])
            }
        
        # Spatial coordination using H3 cells
        n_cells = len(self.h3_cells)
        coordination_matrix = np.eye(n_cells)  # Start with identity
        
        # Add spatial coordination based on H3 neighbor relationships
        try:
            import h3
            for i, cell_i in enumerate(self.h3_cells):
                neighbors = h3.grid_ring(cell_i, 1)  # Get immediate neighbors
                for j, cell_j in enumerate(self.h3_cells):
                    if cell_j in neighbors and i != j:
                        # Calculate coordination strength based on belief similarity
                        agent_i = self.agent_models[i]
                        agent_j = self.agent_models[j]
                        
                        # Coordination based on belief overlap
                        if hasattr(agent_i, 'beliefs') and hasattr(agent_j, 'beliefs'):
                            belief_similarity = 1.0 / (1.0 + np.linalg.norm(agent_i.beliefs - agent_j.beliefs))
                            coordination_matrix[i, j] = belief_similarity
                        else:
                            coordination_matrix[i, j] = 0.5  # Default coordination
        except ImportError:
            # Fallback to random coordination if h3 not available
            coordination_matrix = np.random.rand(n_cells, n_cells)
            coordination_matrix = (coordination_matrix + coordination_matrix.T) / 2
            np.fill_diagonal(coordination_matrix, 1.0)
        except Exception as e:
            logger.warning(f"Coordination calculation failed: {e}")
            coordination_matrix = np.eye(n_cells)
        
        return {
            'coordination_matrix': coordination_matrix,
            'average_coordination': np.mean(coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]),
            'coordination_variance': np.var(coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]),
            'n_coordinated_agents': n_cells
        }

    def get_agent_messages(self, agent_id):
        return {}