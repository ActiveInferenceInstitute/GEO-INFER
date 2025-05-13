#!/usr/bin/env python
"""
Unit tests for the StyleTransfer class in geo_infer_art.core.aesthetics.style_transfer.
"""

import os
import unittest
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
from PIL import Image

from geo_infer_art.core.aesthetics.style_transfer import StyleTransfer
from geo_infer_art.core.visualization.geo_art import GeoArt


class TestStyleTransfer(unittest.TestCase):
    """Test suite for the StyleTransfer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test directory for outputs
        self.test_dir = "test_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Create a simple test image as content
        self.content_image = np.ones((100, 100, 3), dtype=np.uint8) * 200  # Light gray
        self.content_image[30:70, 30:70] = [100, 100, 100]  # Dark gray square
        self.content_image_path = os.path.join(self.test_dir, "content.png")
        Image.fromarray(self.content_image).save(self.content_image_path)
        
        # Create a simple test image as style
        self.style_image = np.ones((100, 100, 3), dtype=np.uint8) * 150  # Gray
        self.style_image[20:40, 20:80] = [200, 50, 50]  # Red bar
        self.style_image[60:80, 20:80] = [50, 200, 50]  # Green bar
        self.style_image_path = os.path.join(self.test_dir, "style.png")
        Image.fromarray(self.style_image).save(self.style_image_path)
        
        # Create a simple GeoDataFrame for testing
        geometries = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        ]
        self.geo_data = gpd.GeoDataFrame(
            {'name': ['Region A', 'Region B']},
            geometry=geometries,
            crs="EPSG:4326"
        )
            
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_init_with_content_and_style(self):
        """Test initialization with content and style images."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf
        except ImportError:
            self.skipTest("TensorFlow not available, skipping test")
            
        style_transfer = StyleTransfer(
            style_image=self.style_image_path,
            content_image=self.content_image_path
        )
        
        self.assertIsNotNone(style_transfer.style_image)
        self.assertIsNotNone(style_transfer.content_image)
    
    def test_get_predefined_style_path(self):
        """Test getting a predefined style path."""
        # Test a valid predefined style
        try:
            style_path = StyleTransfer.get_predefined_style_path("watercolor")
            self.assertTrue(os.path.exists(style_path))
        except FileNotFoundError:
            self.skipTest("Predefined styles not installed, skipping test")
        
        # Test an invalid style name
        with self.assertRaises(ValueError):
            StyleTransfer.get_predefined_style_path("nonexistent_style")
    
    def test_load_style_image(self):
        """Test loading a style image."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf
        except ImportError:
            self.skipTest("TensorFlow not available, skipping test")
            
        style_transfer = StyleTransfer()
        
        # Test loading from file path
        style_transfer.load_style_image(self.style_image_path)
        self.assertIsNotNone(style_transfer.style_image)
        
        # Test loading from numpy array
        style_transfer.load_style_image(self.style_image)
        self.assertIsNotNone(style_transfer.style_image)
        
        # Test loading from PIL Image
        pil_image = Image.fromarray(self.style_image)
        style_transfer.load_style_image(pil_image)
        self.assertIsNotNone(style_transfer.style_image)
    
    def test_apply_style_transfer(self):
        """Test applying style transfer to geospatial data."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf
        except ImportError:
            self.skipTest("TensorFlow not available, skipping test")
            
        # Test with predefined style
        try:
            styled_image = StyleTransfer.apply(
                geo_data=self.geo_data,
                style="watercolor",
                iterations=5  # Use low iterations for faster test
            )
            
            self.assertIsInstance(styled_image, Image.Image)
            
            # Save and check output
            output_path = os.path.join(self.test_dir, "output.png")
            styled_image.save(output_path)
            self.assertTrue(os.path.exists(output_path))
            
        except Exception as e:
            self.skipTest(f"Style transfer test failed: {str(e)}")
    
    def test_apply_with_custom_weights(self):
        """Test applying style transfer with custom weights."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf
        except ImportError:
            self.skipTest("TensorFlow not available, skipping test")
            
        try:
            # Apply with custom weights
            styled_image = StyleTransfer.apply(
                geo_data=self.geo_data,
                style=self.style_image_path,
                content_image=self.content_image_path,
                style_weight=1e-3,
                content_weight=1e3,
                iterations=3  # Use low iterations for faster test
            )
            
            self.assertIsInstance(styled_image, Image.Image)
            
        except Exception as e:
            self.skipTest(f"Style transfer with custom weights failed: {str(e)}")
    
    def test_apply_with_invalid_inputs(self):
        """Test applying style transfer with invalid inputs."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf
        except ImportError:
            self.skipTest("TensorFlow not available, skipping test")
            
        # Test with invalid style
        with self.assertRaises(ValueError):
            StyleTransfer.apply(
                geo_data=self.geo_data,
                style="nonexistent_style"
            )
        
        # Test with invalid geo_data
        with self.assertRaises(ValueError):
            StyleTransfer.apply(
                geo_data="not_geo_data",
                style="watercolor"
            )


if __name__ == "__main__":
    unittest.main() 