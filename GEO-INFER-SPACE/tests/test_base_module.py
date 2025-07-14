import unittest
from pathlib import Path
import json
import shutil
import pytest
from geo_infer_space.core.base_module import BaseAnalysisModule
from geo_infer_space.core.unified_backend import UnifiedH3Backend

class ConcreteModule(BaseAnalysisModule):
    def acquire_raw_data(self) -> Path:
        return Path('test_raw.json')

    def run_final_analysis(self, h3_data: dict) -> dict:
        return {'test_hex': {'value': 1}}

@pytest.mark.core
class TestBaseAnalysisModule(unittest.TestCase):
    def setUp(self):
        self.temp_config_dir = Path('config')
        self.temp_config_dir.mkdir(exist_ok=True)
        config_path = self.temp_config_dir / 'target_areas.geojson'
        sample_geojson = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'properties': {'area': 'TestArea', 'subarea': 'all'},
                'geometry': {'type': 'Polygon', 'coordinates': [[[0,0], [1,0], [1,1], [0,1], [0,0]]] }
            }]
        }
        with open(config_path, 'w') as f:
            json.dump(sample_geojson, f)
        self.backend = UnifiedH3Backend(modules={}, resolution=8, base_data_dir=Path('test_data'))
        self.module = ConcreteModule(self.backend, 'test_module')
        self.module.h3_cache_path.unlink(missing_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_config_dir)

    def test_run_analysis_with_cache(self):
        """Test analysis with pre-existing cache using real file."""
        # Create real cache file
        cache_data = {'test_hex': {}}
        with open(self.module.h3_cache_path, 'w') as f:
            json.dump(cache_data, f)
        result = self.module.run_analysis()
        self.assertEqual(result, {'test_hex': {'value': 1}})
        self.module.h3_cache_path.unlink()  # Cleanup

    def test_run_analysis_no_cache(self):
        """Test analysis without cache, simulating H3 processing."""
        # Simulate raw data file
        raw_path = Path('test_raw.json')
        with open(raw_path, 'w') as f:
            json.dump({}, f)
        # Override acquire to return real path
        self.module.acquire_raw_data = lambda: raw_path
        # Simulate H3 processing
        self.module.process_to_h3 = lambda p: {'test_hex': {}}
        result = self.module.run_analysis()
        self.assertEqual(result, {'test_hex': {'value': 1}})
        raw_path.unlink()  # Cleanup 