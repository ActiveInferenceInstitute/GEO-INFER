import unittest
import numpy as np
import tempfile
from pathlib import Path
from geo_infer_act.utils.config import load_config, save_config, merge_configs, get_config_value
from geo_infer_act.utils.math import softmax, normalize_distribution, kl_divergence, entropy, precision_weighted_error, gaussian_log_likelihood, categorical_log_likelihood, dirichlet_kl_divergence, sample_categorical, compute_free_energy_categorical, compute_expected_free_energy
from geo_infer_act.utils.visualization import plot_belief_update, plot_free_energy, plot_policies, plot_hierarchical_beliefs, plot_markov_blanket
# Add imports for integration if testable

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer
from geo_infer_act.utils.integration import ModernToolsIntegration, integrate_rxinfer, integrate_bayeux, integrate_pymdp, integrate_space, integrate_time, integrate_sim, create_h3_spatial_model, coordinate_multi_agent_system

class TestConfigUtils(unittest.TestCase):
    """Tests for config utilities."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / 'test.yaml'
        self.sample_config = {'key': 'value', 'nested': {'subkey': 42}}

    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()

    def test_save_load_config(self):
        """Test saving and loading config."""
        save_config(self.sample_config, str(self.config_path))
        loaded = load_config(str(self.config_path))
        self.assertEqual(loaded, self.sample_config)

    def test_merge_configs(self):
        """Test merging configs."""
        base = {'a': 1, 'b': {'x': 10}}
        override = {'b': {'x': 20}, 'c': 3}
        merged = merge_configs(base, override)
        self.assertEqual(merged['a'], 1)
        self.assertEqual(merged['b']['x'], 20)
        self.assertEqual(merged['c'], 3)

    def test_get_config_value(self):
        """Test getting nested config value."""
        config = {'section': {'subsection': {'key': 'value'}}}
        value = get_config_value(config, 'section.subsection.key')
        self.assertEqual(value, 'value')
        default_value = get_config_value(config, 'missing.key', default='default')
        self.assertEqual(default_value, 'default')

class TestMathUtils(unittest.TestCase):
    """Tests for math utilities."""

    def test_softmax(self):
        """Test softmax function."""
        x = np.array([1, 2, 3])
        soft = softmax(x)
        self.assertTrue(np.allclose(np.sum(soft), 1.0))
        self.assertTrue(np.all(soft > 0))

    def test_normalize_distribution(self):
        """Test distribution normalization."""
        x = np.array([1, 2, 3])
        norm = normalize_distribution(x)
        self.assertTrue(np.allclose(np.sum(norm), 1.0))
        self.assertTrue(np.allclose(norm, x / np.sum(x)))

    def test_kl_divergence(self):
        """Test KL divergence."""
        p = np.array([0.4, 0.6])
        q = np.array([0.5, 0.5])
        kl = kl_divergence(p, q)
        self.assertGreater(kl, 0)

    def test_kl_divergence_edge(self):
        p = np.array([1,0])
        q = np.array([0.5,0.5])
        div = kl_divergence(p, q)
        self.assertGreater(div, 0)

    def test_entropy(self):
        """Test entropy computation."""
        p = np.array([0.5, 0.5])
        ent = entropy(p)
        self.assertAlmostEqual(ent, np.log(2))

    def test_precision_weighted_error(self):
        """Test precision-weighted error."""
        mean = np.array([0, 0])
        target = np.array([1, 1])
        precision = np.eye(2) * 2
        error = target - mean
        weighted = precision_weighted_error(error, precision)
        self.assertTrue(np.allclose(weighted, np.array([2,2])))

    def test_gaussian_log_likelihood(self):
        """Test Gaussian log likelihood."""
        x = np.array([0, 0])
        mean = np.array([0, 0])
        precision = np.eye(2)
        ll = gaussian_log_likelihood(x, mean, precision)
        self.assertAlmostEqual(ll, -np.log(2*np.pi))

    def test_categorical_log_likelihood(self):
        """Test categorical log likelihood."""
        obs = np.array([1, 0])
        probs = np.array([0.7, 0.3])
        ll = categorical_log_likelihood(obs, probs)
        self.assertAlmostEqual(ll, np.log(0.7))

    def test_dirichlet_kl_divergence(self):
        """Test Dirichlet KL divergence."""
        alpha1 = np.array([1, 1])
        alpha2 = np.array([2, 2])
        kl = dirichlet_kl_divergence(alpha1, alpha2)
        self.assertGreater(kl, 0)

    def test_sample_categorical(self):
        """Test categorical sampling."""
        probs = np.array([0.2, 0.3, 0.5])
        samples = sample_categorical(probs, n_samples=100, random_state=42)
        self.assertEqual(len(samples), 100)
        self.assertTrue(np.all(0 <= samples) and np.all(samples < 3))

    def test_compute_free_energy_categorical(self):
        """Test categorical free energy."""
        beliefs = np.array([0.4, 0.6])
        obs = np.array([0.7, 0.3])
        fe = compute_free_energy_categorical(beliefs, obs)
        self.assertIsInstance(fe, float)

    def test_compute_expected_free_energy(self):
        """Test expected free energy."""
        beliefs = np.array([0.4, 0.6])
        prefs = np.array([0.5, 0.5])
        efe = compute_expected_free_energy(beliefs, prefs)
        self.assertIsInstance(efe, float)

    def test_sample_dirichlet(self):
        alpha = np.array([1,2,3])
        sample = sample_dirichlet(alpha)
        self.assertEqual(len(sample), 3)
        self.assertAlmostEqual(sum(sample), 1.0)

    def test_compute_precision(self):
        error = np.array([0.1,0.2])
        precision = np.array([10,5])
        weighted = precision_weighted_error(error, precision)
        self.assertEqual(len(weighted), 2)

class TestVisualizationUtils(unittest.TestCase):
    """Tests for visualization utilities."""

    def test_plot_belief_update(self):
        """Test belief update plot."""
        before = {'states': np.array([0.3, 0.7])}
        after = {'states': np.array([0.6, 0.4])}
        fig = plot_belief_update(before, after)
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_free_energy(self):
        """Test free energy plot."""
        history = [5.0, 4.0, 3.5, 3.2, 3.1]
        fig = plot_free_energy(history)
        self.assertIsNotNone(fig)
        plt.close(fig)

    def test_plot_policies(self):
        """Test policies plot."""
        probs = np.array([[0.2, 0.3, 0.5], [0.4, 0.4, 0.2]])
        fig = plot_policies(probs)
        self.assertIsNotNone(fig)
        plt.close(fig)

    def test_plot_hierarchical_beliefs(self):
        """Test hierarchical belief plotting."""
        beliefs = {'level_0': np.array([0.4,0.6]), 'level_1': np.array([0.3,0.7])}
        fig = plot_hierarchical_beliefs(beliefs)
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_markov_blanket(self):
        """Test Markov blanket visualization."""
        blanket = {'internal': [0,1], 'sensory': [2,3]}
        fig = plot_markov_blanket(blanket)
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_belief_update_viz(self):
        fig = plot_belief_update(np.array([0.5,0.5]), np.array([0.8,0.2]))
        self.assertIsNotNone(fig)

class TestAnalysisUtils(unittest.TestCase):
    """Tests for analysis utilities."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ActiveInferenceAnalyzer(tempfile.mkdtemp())

    def test_record_step(self):
        """Test recording step."""
        self.analyzer.record_step(np.array([0.5,0.5]), np.array([1,0]), 1, {'policy': {'id':1}}, 1.0)
        self.assertEqual(len(self.analyzer.traces['beliefs']), 1)

    def test_analyze_perception_patterns(self):
        self.analyzer.record_step(np.array([0.5,0.5]), np.array([1,0]), 1, {'policy':{'id':1}}, 1.0)
        analysis = self.analyzer.analyze_perception_patterns()
        self.assertIn('belief_dynamics', analysis)

    def test_analyze_free_energy_patterns(self):
        self.analyzer.record_step(np.array([0.5,0.5]), np.array([1,0]), 1, {'policy':{'id':1}}, 1.0)
        self.analyzer.record_step(np.array([0.6,0.4]), np.array([0,1]), 2, {'policy':{'id':2}}, 0.8)
        analysis = self.analyzer.analyze_free_energy_patterns()
        self.assertIn('minimization_dynamics', analysis)

    # Add tests for analyze_perception_patterns, etc. by calling and checking output structure

class TestIntegrationUtils(unittest.TestCase):
    """Tests for integration utilities."""

    def test_modern_tools_integration(self):
        """Test modern tools."""
        integration = ModernToolsIntegration()
        tools = integration.available_tools
        self.assertIsInstance(tools, dict)

    # Add conditional tests for integrate_rxinfer etc.

    def test_create_h3_spatial_model(self):
        """Test H3 spatial model creation."""
        config = {}
        boundary = {'coordinates': [[[0,0], [0,1], [1,1], [1,0], [0,0]]] }
        result = create_h3_spatial_model(config, 9, boundary)
        if 'error' in result['status']:
            self.assertIn('GEO-INFER-SPACE', result['message'])
        else:
            self.assertEqual(result['status'], 'success')
            self.assertIn('boundary_cells', result['model_config'])

    @unittest.skipUnless(ModernToolsIntegration().available_tools.get('rxinfer', False), 'RxInfer not available')
    def test_integrate_rxinfer(self):
        config = {}
        params = {'model_specification': '@model function test() end', 'data': {'observations': np.random.randn(5)}}
        result = integrate_rxinfer(config, params)
        self.assertEqual(result['status'], 'success')

if __name__ == '__main__':
    unittest.main() 