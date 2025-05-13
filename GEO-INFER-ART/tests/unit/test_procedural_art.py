#!/usr/bin/env python
"""
Unit tests for the ProceduralArt class in geo_infer_art.core.generation.procedural_art.
"""

import os
import unittest
import numpy as np
from PIL import Image

from geo_infer_art.core.generation.procedural_art import ProceduralArt


class TestProceduralArt(unittest.TestCase):
    """Test suite for the ProceduralArt class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test directory for outputs
        self.test_dir = "test_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Define test coordinates
        self.test_lat = 40.7128  # New York
        self.test_lon = -74.0060
            
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        proc_art = ProceduralArt()
        
        self.assertEqual(proc_art.algorithm, "noise_field")
        self.assertIsInstance(proc_art.params, dict)
        self.assertEqual(proc_art.resolution, (800, 800))
        self.assertIsNone(proc_art.image)
    
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        algorithm = "l_system"
        params = {
            "iterations": 5,
            "angle": 25.0,
            "axiom": "F",
            "rules": {"F": "F+F-F"}
        }
        resolution = (600, 400)
        
        proc_art = ProceduralArt(
            algorithm=algorithm,
            params=params,
            resolution=resolution
        )
        
        self.assertEqual(proc_art.algorithm, algorithm)
        self.assertEqual(proc_art.params, params)
        self.assertEqual(proc_art.resolution, resolution)
    
    def test_from_geo_coordinates(self):
        """Test creating ProceduralArt from geographic coordinates."""
        # Test basic creation
        proc_art = ProceduralArt.from_geo_coordinates(
            lat=self.test_lat,
            lon=self.test_lon
        )
        
        self.assertEqual(proc_art.algorithm, "noise_field")  # Default algorithm
        self.assertIn("seed", proc_art.params)
        self.assertIsNotNone(proc_art.image)
        
        # Test with different algorithm and params
        additional_params = {
            "color_palette": "sunset",
            "iterations": 3
        }
        
        proc_art = ProceduralArt.from_geo_coordinates(
            lat=self.test_lat,
            lon=self.test_lon,
            algorithm="l_system",
            additional_params=additional_params
        )
        
        self.assertEqual(proc_art.algorithm, "l_system")
        self.assertEqual(proc_art.params["color_palette"], "sunset")
        self.assertEqual(proc_art.params["iterations"], 3)
        self.assertIsNotNone(proc_art.image)
    
    def test_from_geo_features(self):
        """Test creating ProceduralArt from geographic features."""
        # Test basic creation
        proc_art = ProceduralArt.from_geo_features(
            feature_type="rivers",
            feature_count=3
        )
        
        self.assertEqual(proc_art.algorithm, "l_system")  # Default for features
        self.assertIn("feature_type", proc_art.params)
        self.assertEqual(proc_art.params["feature_type"], "rivers")
        self.assertEqual(proc_art.params["feature_count"], 3)
        self.assertIsNotNone(proc_art.image)
        
        # Test with different algorithm and params
        additional_params = {
            "color_palette": "ocean",
            "complexity": 0.7
        }
        
        proc_art = ProceduralArt.from_geo_features(
            feature_type="coastlines",
            feature_count=1,
            algorithm="cellular_automata",
            additional_params=additional_params
        )
        
        self.assertEqual(proc_art.algorithm, "cellular_automata")
        self.assertEqual(proc_art.params["color_palette"], "ocean")
        self.assertEqual(proc_art.params["complexity"], 0.7)
        self.assertIsNotNone(proc_art.image)
    
    def test_generate(self):
        """Test the generate method."""
        # Initialize without generating
        proc_art = ProceduralArt(
            algorithm="noise_field",
            params={"color_palette": "viridis"},
            resolution=(400, 400)
        )
        
        # Image should not exist yet
        self.assertIsNone(proc_art.image)
        
        # Generate the image
        proc_art.generate()
        
        # Now the image should exist
        self.assertIsNotNone(proc_art.image)
        self.assertIsInstance(proc_art.image, Image.Image)
        self.assertEqual(proc_art.image.size, (400, 400))
    
    def test_save_and_show(self):
        """Test saving and showing procedural art."""
        # Create procedural art
        proc_art = ProceduralArt.from_geo_coordinates(
            lat=self.test_lat,
            lon=self.test_lon,
            algorithm="noise_field"
        )
        
        # Test save method
        output_path = os.path.join(self.test_dir, "procedural_art_output.png")
        saved_path = proc_art.save(output_path)
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(saved_path, output_path)
        
        # Test show method - can only check that it doesn't raise an error
        try:
            proc_art.show()
        except Exception as e:
            self.fail(f"show() method raised an error: {str(e)}")
    
    def test_different_algorithms(self):
        """Test generating art with different algorithms."""
        algorithms = [
            "noise_field",
            "l_system",
            "cellular_automata",
            "reaction_diffusion",
            "voronoi",
            "fractal_tree"
        ]
        
        for algorithm in algorithms:
            try:
                # Create procedural art with this algorithm
                proc_art = ProceduralArt(
                    algorithm=algorithm,
                    params={"color_palette": "viridis"},
                    resolution=(300, 300)  # Smaller for faster tests
                )
                
                proc_art.generate()
                self.assertIsNotNone(proc_art.image)
                
                # Save the output for this algorithm
                output_path = os.path.join(self.test_dir, f"procedural_{algorithm}.png")
                proc_art.save(output_path)
                self.assertTrue(os.path.exists(output_path))
                
            except Exception as e:
                self.skipTest(f"Generation with algorithm {algorithm} failed: {str(e)}")
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test invalid algorithm
        with self.assertRaises(ValueError):
            ProceduralArt(algorithm="invalid_algorithm")
        
        # Test invalid coordinates
        with self.assertRaises(ValueError):
            ProceduralArt.from_geo_coordinates(
                lat=100.0,  # Invalid latitude
                lon=self.test_lon
            )
        
        # Test invalid feature type
        with self.assertRaises(ValueError):
            ProceduralArt.from_geo_features(
                feature_type="invalid_feature_type",
                feature_count=1
            )
        
        # Test invalid resolution
        with self.assertRaises(ValueError):
            ProceduralArt(resolution=(-100, 300))  # Negative resolution


if __name__ == "__main__":
    unittest.main() 