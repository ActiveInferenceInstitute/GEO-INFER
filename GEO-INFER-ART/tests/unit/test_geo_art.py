#!/usr/bin/env python
"""
Unit tests for the GeoArt class in geo_infer_art.core.visualization.geo_art.
"""

import os
import unittest
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

from geo_infer_art.core.visualization.geo_art import GeoArt
from geo_infer_art.core.aesthetics.color_palette import ColorPalette


class TestGeoArt(unittest.TestCase):
    """Test suite for the GeoArt class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test directory for outputs
        self.test_dir = "test_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Create a simple GeoDataFrame for testing
        geometries = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
            Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
        ]
        self.test_data = gpd.GeoDataFrame(
            {'name': ['Region A', 'Region B', 'Region C']},
            geometry=geometries,
            crs="EPSG:4326"
        )
        
        # Create a simple raster for testing
        self.test_raster = np.random.rand(10, 10)
            
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_init_with_vector_data(self):
        """Test initialization with vector data."""
        geo_art = GeoArt(data=self.test_data)
        self.assertEqual(geo_art.crs, "EPSG:4326")
        self.assertIsNotNone(geo_art.data)
        self.assertDictEqual(geo_art.metadata, {})
    
    def test_init_with_raster_data(self):
        """Test initialization with raster data."""
        geo_art = GeoArt(data=self.test_raster)
        self.assertIsNotNone(geo_art.data)
        self.assertDictEqual(geo_art.metadata, {})
    
    def test_apply_style_default(self):
        """Test applying default style."""
        geo_art = GeoArt(data=self.test_data)
        styled = geo_art.apply_style(style="default")
        
        # Check that the figure was created
        self.assertIsNotNone(geo_art._figure)
        self.assertIsNotNone(geo_art._ax)
        
        # Check method chaining
        self.assertEqual(styled, geo_art)
    
    def test_apply_style_with_custom_palette(self):
        """Test applying style with custom color palette."""
        geo_art = GeoArt(data=self.test_data)
        
        # Create a custom palette
        palette = ColorPalette(
            name="custom", 
            colors=["#ff0000", "#00ff00", "#0000ff"]
        )
        
        # Apply style with the palette
        geo_art.apply_style(style="default", color_palette=palette)
        
        # Check that the figure was created
        self.assertIsNotNone(geo_art._figure)
    
    def test_apply_style_with_palette_name(self):
        """Test applying style with a color palette name."""
        geo_art = GeoArt(data=self.test_data)
        geo_art.apply_style(style="default", color_palette="ocean")
        
        # Check that the figure was created
        self.assertIsNotNone(geo_art._figure)
    
    def test_apply_style_with_invalid_data(self):
        """Test applying style with invalid data."""
        geo_art = GeoArt()  # No data
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            geo_art.apply_style()
    
    def test_save(self):
        """Test saving visualization to file."""
        geo_art = GeoArt(data=self.test_data)
        geo_art.apply_style()
        
        output_path = os.path.join(self.test_dir, "test_geo_art.png")
        saved_path = geo_art.save(output_path)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(saved_path, output_path)
    
    def test_save_without_style(self):
        """Test saving without applying style first."""
        geo_art = GeoArt(data=self.test_data)
        
        output_path = os.path.join(self.test_dir, "test_geo_art.png")
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            geo_art.save(output_path)
    
    def test_str_representation(self):
        """Test string representation."""
        # Vector data
        geo_art_vector = GeoArt(data=self.test_data)
        repr_str = repr(geo_art_vector)
        self.assertIn("GeoArt", repr_str)
        self.assertIn("Vector", repr_str)
        self.assertIn("3", repr_str)  # Number of features
        
        # Raster data
        geo_art_raster = GeoArt(data=self.test_raster)
        repr_str = repr(geo_art_raster)
        self.assertIn("GeoArt", repr_str)
        self.assertIn("Raster", repr_str)
    
    def test_load_geojson_file_not_found(self):
        """Test loading GeoJSON with nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            GeoArt.load_geojson("nonexistent_file.geojson")


if __name__ == "__main__":
    unittest.main() 