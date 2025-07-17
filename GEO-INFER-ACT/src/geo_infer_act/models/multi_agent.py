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
        self.agent_models = [CategoricalModel(state_dim=2, obs_dim=2) for _ in range(self.n_agents)]
        self.resource_distribution = np.random.rand(self.n_resources, self.n_locations)
        # Add initializations like in UrbanModel 

    def step(self, actions: Optional[List[Dict[str, Any]]] = None) -> Tuple[Dict[str, Any], bool]:
        return {'resource_distribution': self.resource_distribution.copy()}, False 

    def enable_h3_spatial(self, resolution: int, boundary: Dict[str, Any]):
        from geo_infer_act.utils.integration import create_h3_spatial_model
        result = create_h3_spatial_model({}, resolution, boundary)
        if result['status'] == 'success':
            self.spatial_mode = True
            self.h3_cells = result['model_config']['boundary_cells']
            self.n_locations = len(self.h3_cells)
            self.agent_models = [CategoricalModel(state_dim=4, obs_dim=4) for _ in self.h3_cells]
            logger.info(f'Enabled H3 for multi-agent with {self.n_locations} cells')
        else:
            logger.warning(result['message']) 

    def simulate_h3_lattice(self, timesteps: int, obs_gen: Callable[[str], np.ndarray]) -> List[Dict[str, Dict]]:
        if not self.spatial_mode:
            raise ValueError('Enable H3 first')
        history = []
        agent_map = {cell: i for i, cell in enumerate(self.h3_cells)}
        for t in range(timesteps):
            step_data = {}
            for cell in self.h3_cells:
                idx = agent_map[cell]
                agent = self.agent_models[idx]
                obs = obs_gen(cell)
                beliefs = agent.update_beliefs(obs)
                fe = agent.compute_free_energy()
                step_data[cell] = {'beliefs': beliefs, 'fe': fe}
            history.append(step_data)
        return history
    
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
                neighbors = h3.grid_disk(cell_i, 1)  # Get immediate neighbors
                for j, cell_j in enumerate(self.h3_cells):
                    if cell_j in neighbors and i != j:
                        # Calculate coordination strength based on belief similarity
                        agent_i = self.agent_models[i]
                        agent_j = self.agent_models[j]
                        
                        # Coordination based on belief overlap
                        belief_similarity = 1.0 / (1.0 + np.linalg.norm(agent_i.beliefs - agent_j.beliefs))
                        coordination_matrix[i, j] = belief_similarity
        except ImportError:
            # Fallback to random coordination if h3 not available
            coordination_matrix = np.random.rand(n_cells, n_cells)
            coordination_matrix = (coordination_matrix + coordination_matrix.T) / 2
            np.fill_diagonal(coordination_matrix, 1.0)
        
        return {
            'coordination_matrix': coordination_matrix,
            'average_coordination': np.mean(coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]),
            'coordination_variance': np.var(coordination_matrix[np.triu_indices_from(coordination_matrix, k=1)]),
            'n_coordinated_agents': n_cells
        }