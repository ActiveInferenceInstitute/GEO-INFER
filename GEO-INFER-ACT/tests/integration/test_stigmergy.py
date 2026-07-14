import unittest
import numpy as np
from geo_infer_act.models.multi_agent import MultiAgentModel
from geo_infer_act.utils.geospatial_ai import EnvironmentalActiveInferenceEngine

class TestStigmergicCoordination(unittest.TestCase):
    def test_stigmergy_convergence(self):
        """Behavior-focused test: test_stigmergy_convergence."""
        # 1. Initialize the Environmental Engine
        boundary = {
            "type": "Polygon",
            "coordinates": [[[ -122.41, 37.77 ], [ -122.41, 37.80 ], [ -122.38, 37.80 ], [ -122.38, 37.77 ], [ -122.41, 37.77 ]]]
        }
        
        env_engine = EnvironmentalActiveInferenceEngine(h3_resolution=7, environmental_variables=['vegetation_density', 'human_activity'])
        env_engine.initialize_spatial_domain(boundary)
        
        # 2. Inject some base environmental data
        observations = {}
        for cell in env_engine.environmental_states.keys():
            observations[cell] = {'vegetation_density': 0.8, 'human_activity': 0.0}
        env_engine.observe_environment(observations, timestamp=0.0)
        
        # 3. Create the Multi-Agent Model with the Environmental Engine
        model = MultiAgentModel(n_agents=len(env_engine.environmental_states), environmental_engine=env_engine)
        
        # Enable spatial mode, which will hit the Moran's I spatial priors block
        model.enable_h3_spatial(resolution=7, boundary=boundary)
        
        # Ensure we properly loaded the agents
        self.assertTrue(len(model.agent_models) > 0)
        self.assertTrue(model.spatial_mode)
        
        # 4. Simulate the lattice
        # We write an observation generator that reads from the true environmental state
        def env_observation_generator(cell_id):
            env_state = env_engine.environmental_states.get(cell_id)
            if env_state is None:
                return np.array([0.25, 0.25, 0.25, 0.25])
            
            # The more human_activity, the more we push observation towards index 3 (high temp / high activity proxy)
            activity = getattr(env_state, 'human_activity', 0.0)
            
            # Base observations
            obs = np.array([0.4, 0.3, 0.2, 0.1]) 
            
            # Stigmergic shift based on activity traces left by others
            obs[3] += activity * 2.0 
            obs = obs / np.sum(obs)
            return obs
            
        history = model.simulate_h3_lattice(timesteps=5, obs_gen=env_observation_generator)
        
        # 5. Verify Stigmergic Communication
        # Over 5 timesteps, agents should have positively pulled the human_activity score in the environment
        final_activity_sum = sum([getattr(state, 'human_activity', 0.0) for state in env_engine.environmental_states.values()])
        self.assertTrue(final_activity_sum > 0.0, "Stigmergy failed: Agents did not modify the shared environmental manifold.")

if __name__ == '__main__':
    unittest.main()
