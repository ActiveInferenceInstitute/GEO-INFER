import unittest
from unittest.mock import MagicMock, patch
import json
from pathlib import Path
from geo_infer_space.core.unified_backend import UnifiedH3Backend, BaseAnalysisModule
from geo_infer_space.osc_geo import H3DataLoader

class MockModule(BaseAnalysisModule):
    def acquire_raw_data(self) -> Path:
        return Path('mock_raw.json')

    def run_final_analysis(self, h3_data: dict) -> dict:
        return {'mock_hex': {'value': 42}}

class TestUnifiedH3Backend(unittest.TestCase):
    def setUp(self):
        self.mock_modules = {'mock': MockModule(None, 'mock')}
        self.backend = UnifiedH3Backend(
            modules=self.mock_modules,
            resolution=8,
            target_region='TestRegion',
            target_areas={'TestArea': ['all']},
            base_data_dir=Path('test_data'),
            osc_repo_dir='test_repo'
        )

    @patch('geo_infer_space.core.unified_backend.gpd.read_file')
    def test_define_target_region(self, mock_read_file):
        mock_gdf = MagicMock()
        mock_gdf.unary_union = MagicMock()
        mock_read_file.return_value = mock_gdf
        hex_by_area, all_hex = self.backend._define_target_region({'TestArea': ['all']})
        self.assertIsInstance(hex_by_area, dict)
        self.assertIsInstance(all_hex, list)

    def test_run_comprehensive_analysis(self):
        self.backend.run_comprehensive_analysis()
        self.assertIn('mock', self.backend.unified_data.get('mock_hex', {}))

    def test_get_comprehensive_summary(self):
        summary = self.backend.get_comprehensive_summary()
        self.assertIn('target_region', summary)
        self.assertEqual(summary['target_region'], 'TestRegion') 