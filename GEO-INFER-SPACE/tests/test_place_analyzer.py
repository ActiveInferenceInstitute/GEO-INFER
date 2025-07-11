import unittest
from pathlib import Path
import json
import geopandas as gpd
from geo_infer_space.core.place_analyzer import PlaceAnalyzer
from geo_infer_space.core.spatial_processor import SpatialProcessor

class TestPlaceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path('temp_place_data')
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir = self.temp_dir / 'outputs'
        self.output_dir.mkdir(exist_ok=True)
        # Sample data
        geojson_path = self.temp_dir / 'test.geojson'
        with open(geojson_path, 'w') as f:
            json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}}]}, f)
        self.analyzer = PlaceAnalyzer('TestPlace', self.temp_dir, SpatialProcessor())

    def tearDown(self):
        for root, dirs, files in Path(self.temp_dir).walk(top_down=False):
            for file in files:
                (root / file).unlink()
            for dir in dirs:
                (root / dir).rmdir()
        self.temp_dir.rmdir()

    def test_load_place_data(self):
        """Test loading place data from sources."""
        sources = [{'name': 'test', 'path': str(self.temp_dir / 'test.geojson')}]
        self.analyzer.load_place_data(sources)
        self.assertFalse(self.analyzer.integrated_data.empty)

    def test_perform_spatial_analysis(self):
        """Test performing spatial analysis."""
        sources = [{'name': 'test', 'path': str(self.temp_dir / 'test.geojson')}]
        self.analyzer.load_place_data(sources)
        self.analyzer.perform_spatial_analysis(['buffer'])
        self.assertIn('buffer', self.analyzer.analysis_results) 