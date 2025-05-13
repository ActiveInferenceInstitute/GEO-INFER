"""
Unit tests for the anonymization module.
"""

import unittest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import h3

from geo_infer_sec.core.anonymization import GeospatialAnonymizer


class TestGeospatialAnonymizer(unittest.TestCase):
    """Test cases for GeospatialAnonymizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a small GeoDataFrame with point geometries
        np.random.seed(42)  # For reproducibility
        
        # Generate 10 random points
        latitudes = np.random.uniform(40.0, 41.0, 10)
        longitudes = np.random.uniform(-74.0, -73.0, 10)
        
        # Create GeoDataFrame
        self.points_gdf = gpd.GeoDataFrame(
            {
                'id': range(1, 11),
                'value': np.random.randint(1, 100, 10),
                'name': [f"Point {i}" for i in range(1, 11)],
                'category': np.random.choice(['A', 'B', 'C'], 10),
                'geometry': [Point(lon, lat) for lon, lat in zip(longitudes, latitudes)]
            },
            crs="EPSG:4326"
        )
        
        # Create an anonymizer with fixed seed for reproducibility
        self.anonymizer = GeospatialAnonymizer(seed=42)
        
    def test_location_perturbation(self):
        """Test location perturbation anonymization."""
        # Apply perturbation
        perturbed = self.anonymizer.location_perturbation(self.points_gdf, epsilon=500.0)
        
        # Check that the output is a GeoDataFrame
        self.assertIsInstance(perturbed, gpd.GeoDataFrame)
        
        # Check that the number of rows is preserved
        self.assertEqual(len(perturbed), len(self.points_gdf))
        
        # Check that all attributes are preserved
        self.assertEqual(list(perturbed.columns), list(self.points_gdf.columns))
        
        # Check that geometries are changed
        original_coords = [(p.x, p.y) for p in self.points_gdf.geometry]
        perturbed_coords = [(p.x, p.y) for p in perturbed.geometry]
        
        # At least some coordinates should be different
        differences = [
            np.sqrt((o[0] - p[0])**2 + (o[1] - p[1])**2)
            for o, p in zip(original_coords, perturbed_coords)
        ]
        
        # Check that points were moved
        self.assertTrue(all(d > 0 for d in differences))
        
        # Check that points were not moved too far (within epsilon / 111000 degrees)
        max_degree_shift = 500.0 / 111000
        self.assertTrue(all(d < max_degree_shift for d in differences))
        
    def test_spatial_k_anonymity(self):
        """Test spatial k-anonymity anonymization."""
        # We'll use a larger k than the number of points to force all points into one cell
        k = 20
        anonymized = self.anonymizer.spatial_k_anonymity(
            self.points_gdf, 
            k=k,
            h3_resolution=7
        )
        
        # Check that the output is a GeoDataFrame
        self.assertIsInstance(anonymized, gpd.GeoDataFrame)
        
        # Check that the number of rows is preserved
        self.assertEqual(len(anonymized), len(self.points_gdf))
        
        # Check that all non-geometry attributes are preserved
        for col in self.points_gdf.columns:
            if col != 'geometry':
                self.assertEqual(list(anonymized[col]), list(self.points_gdf[col]))
        
        # Check that there are fewer unique locations in the anonymized data
        original_unique_locs = len(set((p.x, p.y) for p in self.points_gdf.geometry))
        anonymized_unique_locs = len(set((p.x, p.y) for p in anonymized.geometry))
        
        self.assertLessEqual(anonymized_unique_locs, original_unique_locs)
        
        # Since k is larger than our dataset, all points should map to a single location
        self.assertEqual(anonymized_unique_locs, 1)
        
    def test_geographic_masking(self):
        """Test geographic masking anonymization."""
        # Create some admin boundaries (two polygons)
        admin_polygons = [
            Polygon([
                (-74.0, 40.0), (-73.5, 40.0), 
                (-73.5, 40.5), (-74.0, 40.5)
            ]),
            Polygon([
                (-73.5, 40.0), (-73.0, 40.0),
                (-73.0, 40.5), (-73.5, 40.5)
            ])
        ]
        
        admin_gdf = gpd.GeoDataFrame(
            {
                'admin_id': [1, 2],
                'name': ['Region A', 'Region B'],
                'geometry': admin_polygons
            },
            crs="EPSG:4326"
        )
        
        # Apply geographic masking
        masked = self.anonymizer.geographic_masking(
            self.points_gdf,
            attribute_cols=['value', 'category'],
            admin_boundaries=admin_gdf
        )
        
        # Check that the output is a GeoDataFrame
        self.assertIsInstance(masked, gpd.GeoDataFrame)
        
        # Check that the geometries in the result match the admin boundaries
        self.assertEqual(len(masked), len(admin_gdf))
        
        # Check that the result has the aggregated attribute columns
        self.assertIn('value', masked.columns)
        self.assertIn('category', masked.columns)
        
        # The 'name' column should not be in the result since it wasn't in attribute_cols
        self.assertNotIn('name', masked.columns)
        
    def test_non_point_geometries(self):
        """Test that non-point geometries raise an error."""
        # Create a GeoDataFrame with a mix of geometries
        mixed_gdf = gpd.GeoDataFrame(
            {
                'id': [1, 2],
                'geometry': [
                    Point(-73.5, 40.5),
                    Polygon([(-74.0, 40.0), (-73.5, 40.0), (-73.5, 40.5), (-74.0, 40.5)])
                ]
            },
            crs="EPSG:4326"
        )
        
        # Test that location_perturbation raises an error
        with self.assertRaises(ValueError):
            self.anonymizer.location_perturbation(mixed_gdf)
            
        # Test that spatial_k_anonymity raises an error
        with self.assertRaises(ValueError):
            self.anonymizer.spatial_k_anonymity(mixed_gdf)


if __name__ == '__main__':
    unittest.main() 