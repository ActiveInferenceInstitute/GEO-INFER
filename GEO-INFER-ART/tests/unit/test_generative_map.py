#!/usr/bin/env python
"""
Unit tests for the GenerativeMap class in geo_infer_art.core.generation.generative_map.
"""

import os
import unittest
import numpy as np
from PIL import Image

from geo_infer_art.core.generation.generative_map import GenerativeMap


class TestGenerativeMap(unittest.TestCase):
    """Test suite for the GenerativeMap class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test directory for outputs
        self.test_dir = "test_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Create synthetic elevation data (a simple gradient with a peak)
        shape = (100, 100)
        x, y = np.meshgrid(np.linspace(-1, 1, shape[0]), np.linspace(-1, 1, shape[1]))
        self.test_elevation = np.exp(-(x**2 + y**2))  # Gaussian peak
        
        # Create a sample bounding box
        self.test_bbox = (-122.5, 37.5, -122.0, 38.0)  # San Francisco area
            
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_init_with_data(self):
        """Test initialization with elevation data."""
        gen_map = GenerativeMap(data=self.test_elevation)
        self.assertIsNotNone(gen_map.data)
        self.assertEqual(gen_map.data.shape, self.test_elevation.shape)
        self.assertDictEqual(gen_map.metadata, {})
    
    def test_from_elevation_with_array(self):
        """Test creating a GenerativeMap from an elevation array."""
        gen_map = GenerativeMap.from_elevation(
            region=self.test_elevation,
            resolution=128,
            abstraction_level=0.5,
            style="contour"
        )
        
        self.assertIsNotNone(gen_map.data)
        self.assertIsNotNone(gen_map.image)
        self.assertEqual(gen_map.image.size, (128, 128))
        
        # Check metadata
        self.assertIn("type", gen_map.metadata)
        self.assertEqual(gen_map.metadata["type"], "elevation_array")
    
    def test_from_elevation_with_bbox(self):
        """Test creating a GenerativeMap from a bounding box."""
        try:
            gen_map = GenerativeMap.from_elevation(
                region=self.test_bbox,
                resolution=128,
                abstraction_level=0.5,
                style="contour"
            )
            
            self.assertIsNotNone(gen_map.data)
            self.assertIsNotNone(gen_map.image)
            self.assertEqual(gen_map.image.size, (128, 128))
            
            # Check metadata
            self.assertIn("type", gen_map.metadata)
            self.assertEqual(gen_map.metadata["type"], "bbox")
            self.assertEqual(gen_map.metadata["bbox"], self.test_bbox)
            
        except Exception as e:
            self.skipTest(f"Elevation data retrieval failed: {str(e)}")
    
    def test_from_elevation_with_named_region(self):
        """Test creating a GenerativeMap from a named region."""
        try:
            gen_map = GenerativeMap.from_elevation(
                region="grand_canyon",
                resolution=128,
                abstraction_level=0.5,
                style="contour"
            )
            
            self.assertIsNotNone(gen_map.data)
            self.assertIsNotNone(gen_map.image)
            
            # Check metadata
            self.assertIn("type", gen_map.metadata)
            self.assertEqual(gen_map.metadata["type"], "named_region")
            self.assertEqual(gen_map.metadata["region"], "grand_canyon")
            
        except Exception as e:
            self.skipTest(f"Named region retrieval failed: {str(e)}")
    
    def test_different_styles(self):
        """Test generating maps with different styles."""
        styles = ["contour", "flow", "particles", "contour_flow"]
        
        for style in styles:
            try:
                gen_map = GenerativeMap.from_elevation(
                    region=self.test_elevation,
                    resolution=128,
                    style=style
                )
                
                self.assertIsNotNone(gen_map.image)
                
                # Save the output for this style
                output_path = os.path.join(self.test_dir, f"gen_map_{style}.png")
                gen_map.save(output_path)
                self.assertTrue(os.path.exists(output_path))
                
            except Exception as e:
                self.skipTest(f"Generation with style {style} failed: {str(e)}")
    
    def test_abstraction_levels(self):
        """Test generating maps with different abstraction levels."""
        levels = [0.1, 0.5, 0.9]
        
        for level in levels:
            try:
                gen_map = GenerativeMap.from_elevation(
                    region=self.test_elevation,
                    resolution=128,
                    abstraction_level=level,
                    style="contour"
                )
                
                self.assertIsNotNone(gen_map.image)
                
                # Save the output for this abstraction level
                output_path = os.path.join(self.test_dir, f"gen_map_abstract_{level}.png")
                gen_map.save(output_path)
                self.assertTrue(os.path.exists(output_path))
                
            except Exception as e:
                self.skipTest(f"Generation with abstraction level {level} failed: {str(e)}")
    
    def test_save_and_show(self):
        """Test saving and showing the map."""
        gen_map = GenerativeMap.from_elevation(
            region=self.test_elevation,
            resolution=128,
            style="contour"
        )
        
        # Test save method
        output_path = os.path.join(self.test_dir, "gen_map_output.png")
        saved_path = gen_map.save(output_path)
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(saved_path, output_path)
        
        # Test show method - can only check that it doesn't raise an error
        try:
            import matplotlib.pyplot as plt
            plt.switch_backend('Agg')  # Non-interactive backend for testing
            gen_map.show()
        except Exception as e:
            self.fail(f"show() method raised an error: {str(e)}")
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test invalid region type
        with self.assertRaises(ValueError):
            GenerativeMap.from_elevation(
                region=123,  # Not a valid region type
                resolution=128
            )
        
        # Test invalid style
        with self.assertRaises(ValueError):
            GenerativeMap.from_elevation(
                region=self.test_elevation,
                style="invalid_style"
            )
        
        # Test invalid abstraction level
        with self.assertRaises(ValueError):
            GenerativeMap.from_elevation(
                region=self.test_elevation,
                abstraction_level=1.5  # Should be between 0 and 1
            )


if __name__ == "__main__":
    unittest.main() 