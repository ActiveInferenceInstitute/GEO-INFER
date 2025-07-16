import unittest
import numpy as np
from pathlib import Path
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer, create_shared_visualizations
import tempfile

class TestActiveInferenceAnalyzer(unittest.TestCase):
    """Tests for ActiveInferenceAnalyzer."""

    def setUp(self):
        """Set up test fixtures with real data."""
        self.output_dir = Path(tempfile.mkdtemp())
        self.analyzer = ActiveInferenceAnalyzer(str(self.output_dir))
        # Add some real data traces
        for i in range(5):
            beliefs = np.array([0.1 + i*0.1, 0.9 - i*0.1])
            obs = np.array([0.2 + i*0.1, 0.8 - i*0.1])
            actions = i
            policies = {'all_probabilities': np.array([0.3, 0.7]), 'policy': {'id': i}}
            fe = 1.0 - i*0.1
            self.analyzer.record_step(beliefs, obs, actions, policies, fe)

    def test_analyze_perception_patterns(self):
        """Test perception analysis."""
        analysis = self.analyzer.analyze_perception_patterns()
        self.assertIsInstance(analysis, dict)
        self.assertIn('belief_dynamics', analysis)

    def test_analyze_action_selection_patterns(self):
        """Test action selection analysis."""
        analysis = self.analyzer.analyze_action_selection_patterns()
        self.assertIsInstance(analysis, dict)
        self.assertIn('policy_dynamics', analysis)

    def test_analyze_free_energy_patterns(self):
        """Test free energy analysis."""
        analysis = self.analyzer.analyze_free_energy_patterns()
        self.assertIsInstance(analysis, dict)
        self.assertIn('minimization_dynamics', analysis)

    def test_record_step(self):
        """Test recording steps."""
        self.assertEqual(len(self.analyzer.traces['beliefs']), 5)

    def test_save_traces_to_csv(self):
        """Test saving traces."""
        self.analyzer.save_traces_to_csv()
        self.assertTrue((self.output_dir / 'data' / 'beliefs.csv').exists())

    def test_generate_comprehensive_report(self):
        """Test report generation."""
        report = self.analyzer.generate_comprehensive_report()
        self.assertIsInstance(report, str)
        self.assertIn('Active Inference Analysis Report', report)

class TestVisualizationFunctions(unittest.TestCase):
    """Tests for shared visualization functions."""

    def setUp(self):
        """Set up analyzer with data."""
        self.output_dir = Path(tempfile.mkdtemp())
        self.analyzer = ActiveInferenceAnalyzer(str(self.output_dir))
        for i in range(5):
            beliefs = np.array([0.1 + i*0.1, 0.9 - i*0.1])
            obs = np.array([0.2 + i*0.1, 0.8 - i*0.1])
            actions = i
            policies = {'all_probabilities': np.array([0.3, 0.7]), 'policy': {'id': i}}
            fe = 1.0 - i*0.1
            self.analyzer.record_step(beliefs, obs, actions, policies, fe)

    def test_create_shared_visualizations(self):
        """Test creating visualizations."""
        create_shared_visualizations(self.analyzer)
        self.assertTrue((self.output_dir / 'visualizations' / 'belief_evolution_heatmap.png').exists())

if __name__ == '__main__':
    unittest.main() 