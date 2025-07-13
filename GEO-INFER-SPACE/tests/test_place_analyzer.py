import unittest
from pathlib import Path
import json
import geopandas as gpd
from geo_infer_space.core.place_analyzer import PlaceAnalyzer
from geo_infer_space.core.spatial_processor import SpatialProcessor
import shutil
from shapely.geometry import Point

class TestPlaceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path('temp_place_data')
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir = self.temp_dir / 'outputs'
        self.output_dir.mkdir(exist_ok=True)
        # Sample data
        geojson_path = self.temp_dir / 'test.geojson'
        with open(geojson_path, 'w') as f:
            json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 1}, 'geometry': {'type': 'Point', 'coordinates': [0, 0]}}]}, f)
        geojson_path2 = self.temp_dir / 'test2.geojson'
        with open(geojson_path2, 'w') as f:
            json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 2}, 'geometry': {'type': 'Point', 'coordinates': [2, 2]}}]}, f)
        # Simulate a third source (GeoDataFrame to file)
        gdf3 = gpd.GeoDataFrame({'id': [3], 'geometry': [Point(1, 1)]}, crs='EPSG:4326')
        gdf3_path = self.temp_dir / 'test3.shp'
        gdf3.to_file(gdf3_path)
        self.sources = [
            {'name': 'test', 'path': str(geojson_path)},
            {'name': 'test2', 'path': str(geojson_path2)},
            {'name': 'test3', 'path': str(gdf3_path)}
        ]
        self.analyzer = PlaceAnalyzer('TestPlace', self.temp_dir, SpatialProcessor())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_place_data(self):
        """
        Test loading and integrating three sources (two GeoJSON, one Shapefile).
        """
        self.analyzer.load_place_data(self.sources)
        self.assertGreaterEqual(len(self.analyzer.integrated_data), 3)
        self.assertSetEqual(set(self.analyzer.integrated_data['source']), {'test', 'test2', 'test3'})

    def test_perform_spatial_analysis(self):
        """
        Test performing spatial analysis (buffer, proximity, overlay) on integrated data.
        """
        self.analyzer.load_place_data(self.sources)
        self.analyzer.perform_spatial_analysis(['buffer', 'proximity', 'overlay'])
        self.assertIn('buffer', self.analyzer.analysis_results)
        self.assertIn('proximity', self.analyzer.analysis_results)
        self.assertIn('overlay', self.analyzer.analysis_results)
        self.assertIsInstance(self.analyzer.analysis_results['buffer'], gpd.GeoDataFrame)
        # Overlay result should be a GeoDataFrame and not empty
        self.assertIsInstance(self.analyzer.analysis_results['overlay'], gpd.GeoDataFrame)
        self.assertGreater(len(self.analyzer.analysis_results['overlay']), 0) 