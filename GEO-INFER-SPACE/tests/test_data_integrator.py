import unittest
from pathlib import Path
import json
import geopandas as gpd
from geo_infer_space.core.data_integrator import DataIntegrator

class TestDataIntegrator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path('temp_test_data')
        self.temp_dir.mkdir(exist_ok=True)
        # Create sample GeoJSON
        geojson_path = self.temp_dir / 'test.geojson'
        with open(geojson_path, 'w') as f:
            json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}}]}, f)
        # Create sample CSV
        csv_path = self.temp_dir / 'test.csv'
        with open(csv_path, 'w') as f:
            f.write('geometry\nPOINT(1 1)\n')
        self.sources = [{'name': 'geojson', 'path': str(geojson_path)}, {'name': 'csv', 'path': str(csv_path)}]

    def tearDown(self):
        for file in self.temp_dir.iterdir():
            file.unlink()
        self.temp_dir.rmdir()

    def test_integrate_data(self):
        """Test data integration from multiple sources."""
        integrator = DataIntegrator(self.sources)
        integrated = integrator.integrate_data()
        self.assertIsInstance(integrated, gpd.GeoDataFrame)
        self.assertEqual(len(integrated), 2)
        self.assertIn('source', integrated.columns) 