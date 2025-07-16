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

    # Add more tests for private methods if needed

class TestClimateModel(unittest.TestCase):
    """Tests for ClimateModel."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ClimateModel()

    def test_initialization(self):
        """Test initialization."""
        self.assertIsInstance(self.model, ActiveInferenceModel)

    def test_step(self):
        """Test step."""
        result = self.model.step()
        self.assertIsInstance(result, dict)

# Add similar TestCase for EcologicalModel, MultiAgentModel, ResourceModel

if __name__ == '__main__':
    unittest.main() 