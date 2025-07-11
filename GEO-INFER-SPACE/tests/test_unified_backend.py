import unittest
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon
from geo_infer_space.core.unified_backend import UnifiedH3Backend
from geo_infer_space.core.base_module import BaseAnalysisModule

class MockModule(BaseAnalysisModule):
    def acquire_raw_data(self) -> Path:
        return Path('mock_raw.json')

    def run_final_analysis(self, h3_data: dict) -> dict:
        return {'mock_hex': {'value': 42}}

class TestUnifiedH3Backend(unittest.TestCase):
    def setUp(self):
        self.modules = {'mock': MockModule(None, 'mock')}
        self.backend = UnifiedH3Backend(
            modules=self.modules,
            resolution=8,
            target_region='TestRegion',
            target_areas={'TestArea': ['all']},
            base_data_dir=Path('test_data')
        )

    def test_define_target_region(self):
        """Test target region definition with small real geometry."""
        # Small real polygon
        test_geom = {'TestArea': {'all': Polygon([(0,0), (1,0), (1,1), (0,1)])}}
        # Override _get_geometries to return real dict
        self.backend._get_geometries = lambda x: test_geom
        hex_by_area, all_hex = self.backend._define_target_region({'TestArea': ['all']})
        self.assertGreater(len(all_hex), 0)

    def test_run_comprehensive_analysis(self):
        """Test full analysis with small real data."""
        # Set small target hexagons
        self.backend.target_hexagons = ['mock_hex']
        # Simulate module run
        self.backend.modules['mock'].run_analysis = lambda: {'mock_hex': {'value': 42}}
        self.backend.run_comprehensive_analysis()
        self.assertIn('mock', self.backend.unified_data.get('mock_hex', {}))

    def test_get_comprehensive_summary(self):
        """Test summary generation."""
        summary = self.backend.get_comprehensive_summary()
        self.assertIn('target_region', summary)
        self.assertEqual(summary['target_region'], 'TestRegion') 