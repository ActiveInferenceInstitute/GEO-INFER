import unittest
import numpy as np
from geo_infer_act.api.interface import ActiveInferenceInterface
from geo_infer_act.api.client import Client
from geo_infer_act.api.endpoints import create_endpoints

class TestActiveInferenceInterface(unittest.TestCase):
    """Tests for ActiveInferenceInterface."""

    def setUp(self):
        """Set up test fixtures."""
        self.interface = ActiveInferenceInterface()

    def test_create_model_categorical(self):
        """Test creating categorical model."""
        model_id = "test_cat"
        params = {"state_dim": 3, "obs_dim": 2}
        self.interface.create_model(model_id, "categorical", params)
        self.assertIn(model_id, self.interface.models)
        model = self.interface.models[model_id]
        self.assertEqual(model.model_type, "categorical")
        self.assertEqual(model.state_dim, 3)

    def test_update_beliefs_categorical(self):
        """Test updating beliefs for categorical model."""
        model_id = "test_cat_update"
        params = {"state_dim": 3, "obs_dim": 2}
        self.interface.create_model(model_id, "categorical", params)
        observations = {"observations": np.array([1, 0])}
        updated = self.interface.update_beliefs(model_id, observations)
        self.assertIn('states', updated)
        self.assertTrue(np.allclose(np.sum(updated['states']), 1.0))

    def test_select_policy(self):
        """Test policy selection."""
        model_id = "test_policy"
        params = {"state_dim": 3, "obs_dim": 2}
        self.interface.create_model(model_id, "categorical", params)
        result = self.interface.select_policy(model_id)
        self.assertIn('policy', result)
        self.assertIn('probability', result)
        self.assertIn('expected_free_energy', result)
        self.assertTrue(np.allclose(np.sum(result['all_probabilities']), 1.0))

    def test_set_preferences(self):
        """Test setting preferences."""
        model_id = "test_prefs"
        params = {"state_dim": 3, "obs_dim": 2}
        self.interface.create_model(model_id, "categorical", params)
        prefs = {"observations": np.array([0.1, 0.9])}
        self.interface.set_preferences(model_id, prefs)
        model = self.interface.models[model_id]
        self.assertTrue(np.allclose(model.preferences['observations'], [0.1, 0.9]))

    def test_get_free_energy(self):
        """Test getting free energy."""
        model_id = "test_fe"
        params = {"state_dim": 3, "obs_dim": 2}
        self.interface.create_model(model_id, "categorical", params)
        fe = self.interface.get_free_energy(model_id)
        self.assertIsInstance(fe, float)

    # Add tests for Gaussian and hierarchical

class TestClient(unittest.TestCase):
    """Tests for API Client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client(base_url="http://test")  # Mock URL

    # Since it uses requests, might need mocking, but according to rules no mocks, so perhaps skip or assume server.

    def test_initialization(self):
        """Test client initializes."""
        self.assertEqual(self.client.base_url, "http://test")

# Test endpoints function
class TestEndpoints(unittest.TestCase):
    """Tests for API endpoints."""

    def test_create_endpoints(self):
        """Test creating endpoints."""
        endpoints = create_endpoints()
        self.assertIn("models", endpoints)
        self.assertIn("beliefs", endpoints)
        self.assertIn("policies", endpoints)

if __name__ == '__main__':
    unittest.main() 