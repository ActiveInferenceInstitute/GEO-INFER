import unittest
from unittest.mock import patch
from pathlib import Path
from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine

class TestInteractiveVisualizationEngine(unittest.TestCase):
    def setUp(self):
        self.config = {'location': {'bounds': {'north': 42, 'south': 41, 'east': -123, 'west': -125}}}
        self.engine = InteractiveVisualizationEngine(self.config, Path('test_output'))

    def test_initialization(self):
        self.assertEqual(self.engine.center_lat, 41.5)
        self.assertEqual(self.engine.center_lon, -124.0)

    @patch('folium.Map')
    def test_create_base_map(self, mock_map):
        mock_map.return_value = 'mock_map'
        base_map = self.engine.create_base_map()
        self.assertEqual(base_map, 'mock_map') 