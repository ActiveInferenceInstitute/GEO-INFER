import unittest
from pathlib import Path
from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine

class TestInteractiveVisualizationEngine(unittest.TestCase):
    def setUp(self):
        self.config = {'location': {'bounds': {'north': 42, 'south': 41, 'east': -123, 'west': -125}}}
        self.engine = InteractiveVisualizationEngine(self.config, Path('test_output'))

    def test_initialization(self):
        """Test engine initialization with config."""
        self.assertEqual(self.engine.center_lat, 41.5)
        self.assertEqual(self.engine.center_lon, -124.0)

    def test_create_comprehensive_dashboard(self):
        """Test dashboard creation with small real data."""
        analysis_results = {'domain_results': {'forest_health': {}}}
        dashboard_path = self.engine.create_comprehensive_dashboard(analysis_results)
        self.assertTrue(Path(dashboard_path).exists()) 