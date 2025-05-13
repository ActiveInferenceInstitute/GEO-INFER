#!/usr/bin/env python
"""
Unit tests for the ColorPalette class in geo_infer_art.core.aesthetics.color_palette.
"""

import os
import unittest
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from geo_infer_art.core.aesthetics.color_palette import ColorPalette


class TestColorPalette(unittest.TestCase):
    """Test suite for the ColorPalette class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test directory for outputs
        self.test_dir = "test_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_init_with_default_palette(self):
        """Test initialization with default palette."""
        palette = ColorPalette()
        self.assertEqual(palette.name, "viridis")
        self.assertIsNotNone(palette.colors)
        self.assertIsInstance(palette.cmap, LinearSegmentedColormap)
    
    def test_init_with_custom_colors(self):
        """Test initialization with custom colors."""
        custom_colors = ["#ff0000", "#00ff00", "#0000ff"]
        palette = ColorPalette(name="custom", colors=custom_colors)
        self.assertEqual(palette.name, "custom")
        self.assertEqual(palette.colors, custom_colors)
        self.assertIsInstance(palette.cmap, LinearSegmentedColormap)
    
    def test_get_palette(self):
        """Test getting a predefined palette."""
        # Test valid palette name
        palette = ColorPalette.get_palette("ocean")
        self.assertEqual(palette.name, "ocean")
        self.assertIsNotNone(palette.colors)
        
        # Test invalid palette name
        with self.assertRaises(ValueError):
            ColorPalette.get_palette("nonexistent_palette")
    
    def test_from_color_theory(self):
        """Test creating a palette from color theory."""
        base_color = "#1a5276"  # A dark blue
        
        # Test complementary scheme
        palette = ColorPalette.from_color_theory(
            base_color=base_color,
            scheme="complementary",
            n_colors=4
        )
        self.assertTrue(palette.name.startswith("complementary"))
        self.assertEqual(len(palette.colors), 4)
        
        # Test analogous scheme
        palette = ColorPalette.from_color_theory(
            base_color=base_color,
            scheme="analogous",
            n_colors=5
        )
        self.assertTrue(palette.name.startswith("analogous"))
        self.assertEqual(len(palette.colors), 5)
        
        # Test invalid scheme
        with self.assertRaises(ValueError):
            ColorPalette.from_color_theory(
                base_color=base_color,
                scheme="invalid_scheme"
            )
    
    def test_invert(self):
        """Test inverting a palette."""
        original = ColorPalette.get_palette("viridis")
        inverted = original.invert()
        
        # Check that name is updated
        self.assertEqual(inverted.name, "viridis_inverted")
        
        # Check that colors are reversed
        self.assertEqual(inverted.colors, original.colors[::-1])
        
    def test_cmap_creation(self):
        """Test that the colormap is properly created."""
        palette = ColorPalette(name="test", colors=["red", "green", "blue"])
        
        # Verify the colormap has the correct name
        self.assertEqual(palette.cmap.name, "test")
        
        # Verify the colormap can be used to map values
        values = np.linspace(0, 1, 10)
        mapped_colors = palette.cmap(values)
        self.assertEqual(mapped_colors.shape, (10, 4))  # RGBA values
        
    def test_str_representation(self):
        """Test string representation of ColorPalette."""
        palette = ColorPalette(name="test", colors=["red", "green", "blue"])
        repr_str = repr(palette)
        self.assertIn("ColorPalette", repr_str)
        self.assertIn("test", repr_str)
        self.assertIn("3", repr_str)  # Number of colors


if __name__ == "__main__":
    unittest.main() 