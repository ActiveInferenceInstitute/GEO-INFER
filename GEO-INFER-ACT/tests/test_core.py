"""
Tests for GEO-INFER-ACT core functionality.
"""
import os
import sys
import unittest
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.geo_infer_act.core.generative_model import GenerativeModel
from src.geo_infer_act.core.free_energy import FreeEnergy, ExpectedFreeEnergy
from src.geo_infer_act.core.policy_selection import PolicySelection


class TestGenerativeModel(unittest.TestCase):
    """Test the GenerativeModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.categorical_params = {
            "state_dim": 3,
            "obs_dim": 2,
            "prior_precision": 1.0
        }
        
        self.gaussian_params = {
            "state_dim": 2,
            "obs_dim": 2,
            "prior_precision": 1.0
        }
        
        self.cat_model = GenerativeModel(
            model_type="categorical",
            parameters=self.categorical_params
        )
        
        self.gauss_model = GenerativeModel(
            model_type="gaussian",
            parameters=self.gaussian_params
        )
    
    def test_initialization(self):
        """Test that models initialize correctly."""
        # Test categorical model
        self.assertEqual(self.cat_model.state_dim, 3)
        self.assertEqual(self.cat_model.obs_dim, 2)
        self.assertEqual(self.cat_model.model_type, "categorical")
        
        # Check that beliefs are initialized properly
        self.assertIn('states', self.cat_model.beliefs)
        self.assertEqual(len(self.cat_model.beliefs['states']), 3)
        
        # Test Gaussian model
        self.assertEqual(self.gauss_model.state_dim, 2)
        self.assertEqual(self.gauss_model.obs_dim, 2)
        self.assertEqual(self.gauss_model.model_type, "gaussian")
        
        # Check that beliefs are initialized properly
        self.assertIn('mean', self.gauss_model.beliefs)
        self.assertEqual(len(self.gauss_model.beliefs['mean']), 2)
    
    def test_belief_updating_categorical(self):
        """Test belief updating for categorical model."""
        # Initial uniform belief
        initial_belief = self.cat_model.beliefs['states'].copy()
        self.assertTrue(np.allclose(initial_belief, np.array([1/3, 1/3, 1/3])))
        
        # Update with an observation
        observation = {"observations": np.array([1, 0])}
        updated_beliefs = self.cat_model.update_beliefs(observation)
        
        # Ensure beliefs have changed
        self.assertFalse(np.allclose(updated_beliefs['states'], initial_belief))
        
        # Ensure still a valid probability distribution
        self.assertTrue(np.allclose(np.sum(updated_beliefs['states']), 1.0))
    
    def test_belief_updating_gaussian(self):
        """Test belief updating for Gaussian model."""
        # Initial zero mean belief
        initial_mean = self.gauss_model.beliefs['mean'].copy()
        self.assertTrue(np.allclose(initial_mean, np.array([0, 0])))
        
        # Update with an observation
        observation = {"observations": np.array([1, 1])}
        updated_beliefs = self.gauss_model.update_beliefs(observation)
        
        # Ensure beliefs have changed
        self.assertFalse(np.allclose(updated_beliefs['mean'], initial_mean))
    
    def test_compute_free_energy(self):
        """Test computation of free energy."""
        # Just ensure it runs without error and returns a float
        fe = self.cat_model.compute_free_energy()
        self.assertIsInstance(fe, float)
        
        fe = self.gauss_model.compute_free_energy()
        self.assertIsInstance(fe, float)


class TestPolicySelection(unittest.TestCase):
    """Test the PolicySelection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.params = {
            "state_dim": 3,
            "obs_dim": 2,
            "prior_precision": 1.0
        }
        
        self.model = GenerativeModel(
            model_type="categorical",
            parameters=self.params
        )
        
        self.policy_selector = PolicySelection(
            generative_model=self.model
        )
    
    def test_initialization(self):
        """Test that policy selector initializes correctly."""
        self.assertEqual(self.policy_selector.model, self.model)
        self.assertIsNotNone(self.policy_selector.policies)
        self.assertGreater(len(self.policy_selector.policies), 0)
    
    def test_select_policy(self):
        """Test policy selection."""
        # Update the model beliefs first
        observation = {"observations": np.array([1, 0])}
        self.model.update_beliefs(observation)
        
        # Select policy
        result = self.policy_selector.select_policy()
        
        # Check result structure
        self.assertIn('policy', result)
        self.assertIn('probability', result)
        self.assertIn('expected_free_energy', result)
        self.assertIn('all_probabilities', result)
        
        # Check that probabilities sum to 1
        self.assertTrue(np.allclose(np.sum(result['all_probabilities']), 1.0))
        
        # Check that the best policy is the one with max probability
        best_idx = np.argmax(result['all_probabilities'])
        self.assertEqual(result['policy'], self.policy_selector.policies[best_idx])


if __name__ == '__main__':
    unittest.main() 