import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from geo_infer_space.core.base_module import BaseAnalysisModule
from geo_infer_space.core.unified_backend import UnifiedH3Backend

class ConcreteModule(BaseAnalysisModule):
    def acquire_raw_data(self) -> Path:
        return Path('test_raw.json')

    def run_final_analysis(self, h3_data: dict) -> dict:
        return {'test_hex': {'value': 1}}

class TestBaseAnalysisModule(unittest.TestCase):
    def setUp(self):
        self.mock_backend = MagicMock(spec=UnifiedH3Backend)
        self.mock_backend.resolution = 8
        self.mock_backend.target_hexagons = ['test_hex']
        self.mock_backend.h3_loader = MagicMock()
        self.module = ConcreteModule(self.mock_backend, 'test_module')

    @patch('geo_infer_space.core.base_module.json.load')
    @patch('builtins.open')
    def test_run_analysis_with_cache(self, mock_open, mock_json_load):
        self.module.h3_cache_path.exists.return_value = True
        mock_json_load.return_value = {'test_hex': {}}
        result = self.module.run_analysis()
        self.assertEqual(result, {'test_hex': {'value': 1}})

    def test_run_analysis_no_cache(self):
        self.module.h3_cache_path.exists.return_value = False
        self.mock_backend.h3_loader.load_data.return_value = {'test_hex': {}}
        result = self.module.run_analysis()
        self.assertEqual(result, {'test_hex': {'value': 1}}) 