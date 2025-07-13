import unittest
from pathlib import Path
import json
import geopandas as gpd
from shapely.geometry import Point
from geo_infer_space.core.data_integrator import DataIntegrator
import pandas as pd

class TestDataIntegrator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path('temp_test_data')
        self.temp_dir.mkdir(exist_ok=True)
        # Create sample GeoJSON (EPSG:4326)
        geojson_path = self.temp_dir / 'test.geojson'
        geojson_data = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [0, 0]},
                'properties': {'id': 1, 'value': 10}
            }]
        }
        with open(geojson_path, 'w') as f:
            json.dump(geojson_data, f)
        # Create sample CSV (geometry as WKT, different CRS)
        csv_path = self.temp_dir / 'test.csv'
        df_csv = pd.DataFrame({
            'id': [2],
            'value': [20],
            'geometry': ['POINT(1 1)']
        })
        df_csv.to_csv(csv_path, index=False)
        # Create simulated Shapefile (GeoDataFrame, EPSG:3857)
        shp_path = self.temp_dir / 'test.shp'
        gdf_shp = gpd.GeoDataFrame({
            'id': [3],
            'value': [30],
            'geometry': [Point(2, 2)]
        }, crs='EPSG:3857')
        gdf_shp.to_file(shp_path)
        self.sources = [
            {'name': 'geojson', 'path': str(geojson_path)},
            {'name': 'csv', 'path': str(csv_path)},
            {'name': 'shapefile', 'path': str(shp_path)}
        ]

    def tearDown(self):
        for file in self.temp_dir.iterdir():
            file.unlink()
        self.temp_dir.rmdir()

    def test_integrate_data(self):
        """
        Test data integration from multiple sources (GeoJSON, CSV, Shapefile),
        CRS harmonization, and attribute fusion.
        """
        integrator = DataIntegrator(self.sources)
        integrated = integrator.integrate_data()
        # Check type and row count
        self.assertIsInstance(integrated, gpd.GeoDataFrame)
        self.assertEqual(len(integrated), 3)
        self.assertIn('source', integrated.columns)
        self.assertIn('id', integrated.columns)
        self.assertIn('value', integrated.columns)
        # Check CRS is harmonized (should be set, likely EPSG:4326)
        self.assertTrue(integrated.crs is not None)
        # Check all sources are present
        self.assertSetEqual(set(integrated['source']), {'geojson', 'csv', 'shapefile'})
        # Check attribute fusion: join on 'id' and sum 'value'
        merged = integrated.groupby('id').agg({'value': 'sum'}).reset_index()
        self.assertEqual(merged['value'].sum(), 60) 