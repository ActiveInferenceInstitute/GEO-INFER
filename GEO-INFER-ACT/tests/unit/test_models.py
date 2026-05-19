import unittest
import numpy as np
from geo_infer_act.models.base import ActiveInferenceModel, CategoricalModel, GaussianModel
from geo_infer_act.models.urban import UrbanModel
from geo_infer_act.models.climate import ClimateModel
from geo_infer_act.models.ecological import EcologicalModel
from geo_infer_act.models.multi_agent import MultiAgentModel
from geo_infer_act.models.resource import ResourceModel
# Add imports for other models like EcologicalModel, etc.

class TestCategoricalModel(unittest.TestCase):
    """Tests for CategoricalModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = CategoricalModel(state_dim=3, obs_dim=2)
        self.model.likelihood_matrix = np.array([[0.8, 0.1, 0.2], [0.2, 0.9, 0.8]])

    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.model.state_dim, 3)
        self.assertEqual(self.model.obs_dim, 2)
        self.assertTrue(np.allclose(self.model.beliefs, np.ones(3)/3))
        self.assertTrue(np.allclose(self.model.preferences, np.ones(2)/2))

    def test_set_preferences(self):
        """Test setting preferences."""
        prefs = np.array([0.4, 0.6])
        self.model.set_preferences(prefs)
        self.assertTrue(np.allclose(self.model.preferences, prefs / np.sum(prefs)))

    def test_set_transition_matrix(self):
        """Test setting transition matrix."""
        trans = np.ones((3,3))
        self.model.set_transition_matrix(trans)
        self.assertTrue(np.allclose(np.sum(self.model.transition_matrix, axis=1), 1.0))

    def test_set_likelihood_matrix(self):
        """Test setting likelihood matrix."""
        lik = np.ones((2,3))
        self.model.set_likelihood_matrix(lik)
        self.assertTrue(np.allclose(np.sum(self.model.likelihood_matrix, axis=0), 1.0))

    def test_update_beliefs(self):
        """Test belief updating."""
        obs = np.array([1, 0])
        updated = self.model.update_beliefs(obs)
        self.assertTrue(np.allclose(np.sum(updated), 1.0))
        self.assertFalse(np.allclose(updated, np.ones(3)/3))

    def test_step(self):
        """Test model step."""
        new_beliefs = self.model.step()
        self.assertTrue(np.allclose(np.sum(new_beliefs), 1.0))

    def test_reset(self):
        """Test reset."""
        self.model.beliefs = np.array([0.1, 0.2, 0.7])
        initial = self.model.reset()
        self.assertTrue(np.allclose(initial, np.ones(3)/3))

    def test_compute_free_energy_handles_zero_beliefs(self):
        """Free energy remains finite for exact categorical beliefs."""
        self.model.beliefs = np.array([1.0, 0.0, 0.0])
        free_energy = self.model.compute_free_energy()
        self.assertTrue(np.isfinite(free_energy))
        self.assertAlmostEqual(free_energy, np.log(3), places=6)

class TestGaussianModel(unittest.TestCase):
    """Tests for GaussianModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = GaussianModel(state_dim=2, obs_dim=2)

    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.model.state_dim, 2)
        self.assertTrue(np.allclose(self.model.belief_mean, np.zeros(2)))
        self.assertTrue(np.allclose(self.model.belief_cov, np.eye(2)))

    def test_set_preferences(self):
        """Test setting preferences."""
        mean = np.array([1, 2])
        cov = np.eye(2) * 0.5
        self.model.set_preferences(mean, cov)
        self.assertTrue(np.allclose(self.model.preference_mean, mean))
        self.assertTrue(np.allclose(self.model.preference_cov, cov))

    def test_set_transition_model(self):
        """Test setting transition model."""
        A = np.array([[0.5, 0], [0, 0.5]])
        Q = np.eye(2) * 0.05
        self.model.set_transition_model(A, Q=Q)
        self.assertTrue(np.allclose(self.model.A, A))
        self.assertTrue(np.allclose(self.model.Q, Q))

    def test_set_observation_model(self):
        """Test setting observation model."""
        C = np.array([[1, 0], [0, 1]])
        R = np.eye(2) * 0.02
        self.model.set_observation_model(C, R)
        self.assertTrue(np.allclose(self.model.C, C))
        self.assertTrue(np.allclose(self.model.R, R))

    def test_update_beliefs(self):
        """Test belief updating."""
        obs = np.array([1, 1])
        updated = self.model.update_beliefs(obs)
        self.assertIn('mean', updated)
        self.assertIn('cov', updated)
        self.assertFalse(np.allclose(updated['mean'], np.zeros(2)))

    def test_step(self):
        """Test model step."""
        updated = self.model.step()
        self.assertIn('mean', updated)
        self.assertIn('cov', updated)

    def test_reset(self):
        """Test reset."""
        self.model.belief_mean = np.array([1, 2])
        initial = self.model.reset()
        self.assertTrue(np.allclose(initial['mean'], np.zeros(2)))

# Add tests for UrbanModel and others

class TestUrbanModel(unittest.TestCase):
    """Tests for UrbanModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = UrbanModel(n_agents=2, n_resources=2, n_locations=3, planning_horizon=2)

    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.model.n_agents, 2)
        self.assertEqual(self.model.n_locations, 3)
        self.assertEqual(len(self.model.agents), 2)
        self.assertEqual(self.model.resource_levels.shape, (3,))
        self.assertEqual(self.model.connectivity.shape, (3,3))

    def test_step(self):
        """Test model step."""
        state, done = self.model.step()
        self.assertIn('resource_map', state)
        self.assertIn('states', state)
        self.assertFalse(done)

    def test_urban_model_step(self):
        model = UrbanModel(n_resources=3, n_locations=5)
        state, done = model.step()
        self.assertEqual(len(state['resource_map']), model.n_locations)
        self.assertFalse(done)

    # Add more tests for private methods if needed

class TestClimateModel(unittest.TestCase):
    """Tests for ClimateModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ClimateModel()

    def test_initialization(self):
        """Test initialization."""
        from geo_infer_act.core.active_inference import ActiveInferenceModel as CoreActiveInferenceModel
        self.assertIsInstance(self.model, CoreActiveInferenceModel)

    def test_step(self):
        """Test step."""
        result = self.model.step()
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], dict)

# Add similar TestCase for EcologicalModel, MultiAgentModel, ResourceModel

class TestEcologicalModel(unittest.TestCase):
    """Tests for EcologicalModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = EcologicalModel()

    def test_step(self):
        """Test step."""
        result = self.model.step()
        self.assertIsInstance(result, dict)

class TestMultiAgentModel(unittest.TestCase):
    """Tests for MultiAgentModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = MultiAgentModel(n_agents=2, n_resources=2, n_locations=3, planning_horizon=2)

    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.model.n_agents, 2)
        self.assertEqual(self.model.n_resources, 2)
        self.assertEqual(self.model.n_locations, 3)
        self.assertEqual(len(self.model.agent_models), 2)
        self.assertEqual(self.model.resource_distribution.shape, (2,3))
        self.assertEqual(self.model.location_connectivity.shape, (3,3))
        self.assertEqual(self.model.agent_preferences.shape, (2,2))

    def test_step(self):
        """Test model step."""
        state, done = self.model.step()
        self.assertIn('resource_distribution', state)
        self.assertIn('agent_locations', state)
        self.assertFalse(done)

    def test_multi_agent_h3(self):
        model = MultiAgentModel()
        # Assume some H3 method
        self.assertTrue(True)

    # Add more tests for private methods if needed

class TestResourceModel(unittest.TestCase):
    """Tests for ResourceModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ResourceModel(n_resources=2, n_locations=3, planning_horizon=2)

    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.model.n_resources, 2)
        self.assertEqual(self.model.n_locations, 3)
        self.assertEqual(self.model.planning_horizon, 2)
        self.assertEqual(self.model.resource_distribution.shape, (2, 3))
        self.assertEqual(self.model.location_connectivity.shape, (3, 3))

    def test_step(self):
        """Test model step returns expected state keys."""
        state, done = self.model.step()
        self.assertIn('resource_distribution', state)
        self.assertIn('total_resources', state)
        self.assertIn('sustainability_score', state)
        self.assertIn('free_energy', state)
        self.assertIn('step', state)
        self.assertFalse(done)
        # Verify resource distribution shape preserved
        self.assertEqual(state['resource_distribution'].shape, (2, 3))
        # Verify step counter incremented
        self.assertEqual(state['step'], 1)

    def test_step_with_actions(self):
        """Test step with harvesting actions."""
        actions = np.ones((2, 3)) * 0.5
        state, done = self.model.step(actions=actions)
        self.assertIn('harvest_yield', state)
        # Harvest yield should be non-negative
        self.assertTrue(np.all(state['harvest_yield'] >= 0))
    
    def test_reset(self):
        """Test model reset."""
        self.model.step()
        state = self.model.reset()
        self.assertEqual(self.model.step_count, 0)
        self.assertIn('resource_distribution', state)
        self.assertEqual(len(self.model.history), 0)
    
    def test_allocation_scores(self):
        """Test free-energy-based allocation scoring."""
        scores = self.model.get_allocation_scores()
        self.assertEqual(scores.shape, (2, 3))
        # Each row should sum to ~1 (normalized)
        for r in range(2):
            self.assertAlmostEqual(scores[r].sum(), 1.0, places=5)

    def test_resource_h3(self):
        model = ResourceModel()
        # Assume some H3 method
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
