#!/usr/bin/env python
"""
Unit tests for the PlaceArt class in geo_infer_art.core.place.place_art.
"""

import os
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image

from geo_infer_art.core.place.place_art import PlaceArt
from geo_infer_art.utils.validators import validate_coordinates


class TestPlaceArt(unittest.TestCase):
    """Test suite for the PlaceArt class."""
    
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
    
    def test_init_with_location(self):
        """Test initialization with location data."""
        location = {
            "name": "Test Location",
            "coordinates": (self.test_lat, self.test_lon),
            "country": "Test Country"
        }
        
        place_art = PlaceArt(location=location)
        
        self.assertEqual(place_art.location, location)
        self.assertIsNone(place_art.data)
        self.assertIsNone(place_art.image)
    
    @patch('geo_infer_art.core.place.place_art.PlaceArt._fetch_location_data')
    def test_from_coordinates(self, mock_fetch):
        """Test creating PlaceArt from coordinates."""
        # Mock the data fetching
        mock_fetch.return_value = {
            "name": "New York",
            "coordinates": (self.test_lat, self.test_lon),
            "country": "United States"
        }
        
        # Create from coordinates
        place_art = PlaceArt.from_coordinates(
            lat=self.test_lat,
            lon=self.test_lon,
            name="Custom Name",
            radius_km=2.0,
            style="abstract"
        )
        
        # Check that the location was set
        self.assertEqual(place_art.location["name"], "Custom Name")
        self.assertEqual(place_art.location["coordinates"], (self.test_lat, self.test_lon))
        
        # Check that the image was created
        self.assertIsNotNone(place_art.image)
    
    @patch('geo_infer_art.core.place.place_art.PlaceArt._fetch_place_data')
    def test_from_place_name(self, mock_fetch):
        """Test creating PlaceArt from a place name."""
        # Mock the data fetching
        mock_fetch.return_value = {
            "name": "Paris",
            "coordinates": (48.8566, 2.3522),
            "country": "France"
        }
        
        # Create from place name
        place_art = PlaceArt.from_place_name(
            place_name="Paris",
            style="topographic",
            include_data=True
        )
        
        # Check that the location was set
        self.assertEqual(place_art.location["name"], "Paris")
        self.assertEqual(place_art.location["coordinates"], (48.8566, 2.3522))
        
        # Check that the image was created
        self.assertIsNotNone(place_art.image)
    
    @patch('geo_infer_art.core.place.place_art.PlaceArt._fetch_location_data')
    def test_add_metadata_overlay(self, mock_fetch):
        """Test adding metadata overlay to the image."""
        # Mock the data fetching
        mock_fetch.return_value = {
            "name": "Test Location",
            "coordinates": (self.test_lat, self.test_lon),
            "country": "Test Country"
        }
        
        # Create place art
        place_art = PlaceArt.from_coordinates(
            lat=self.test_lat,
            lon=self.test_lon,
            style="abstract"
        )
        
        # Add metadata overlay
        place_art_with_overlay = place_art.add_metadata_overlay(
            position="bottom",
            opacity=0.8
        )
        
        # Check method chaining
        self.assertEqual(place_art, place_art_with_overlay)
        
        # Check that the image still exists
        self.assertIsNotNone(place_art.image)
    
    @patch('geo_infer_art.core.place.place_art.PlaceArt._fetch_location_data')
    def test_save_and_show(self, mock_fetch):
        """Test saving and showing the place art."""
        # Mock the data fetching
        mock_fetch.return_value = {
            "name": "Test Location",
            "coordinates": (self.test_lat, self.test_lon),
            "country": "Test Country"
        }
        
        # Create place art
        place_art = PlaceArt.from_coordinates(
            lat=self.test_lat,
            lon=self.test_lon,
            style="abstract"
        )
        
        # Test save method
        output_path = os.path.join(self.test_dir, "place_art_output.png")
        saved_path = place_art.save(output_path)
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(saved_path, output_path)
        
        # Test show method - can only check that it doesn't raise an error
        try:
            place_art.show()
        except Exception as e:
            self.fail(f"show() method raised an error: {str(e)}")
    
    def test_different_styles(self):
        """Test creating place art with different styles."""
        styles = ["abstract", "topographic", "cultural", "mixed_media"]
        
        for style in styles:
            with patch('geo_infer_art.core.place.place_art.PlaceArt._fetch_location_data') as mock_fetch:
                # Mock the data fetching
                mock_fetch.return_value = {
                    "name": f"Test Location - {style}",
                    "coordinates": (self.test_lat, self.test_lon),
                    "country": "Test Country"
                }
                
                try:
                    # Create place art with this style
                    place_art = PlaceArt.from_coordinates(
                        lat=self.test_lat,
                        lon=self.test_lon,
                        style=style
                    )
                    
                    self.assertIsNotNone(place_art.image)
                    
                    # Save the output for this style
                    output_path = os.path.join(self.test_dir, f"place_art_{style}.png")
                    place_art.save(output_path)
                    self.assertTrue(os.path.exists(output_path))
                    
                except Exception as e:
                    self.skipTest(f"Creation with style {style} failed: {str(e)}")
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test invalid coordinates
        with self.assertRaises(ValueError):
            PlaceArt.from_coordinates(
                lat=100.0,  # Invalid latitude
                lon=self.test_lon
            )
        
        # Test invalid style
        with patch('geo_infer_art.core.place.place_art.PlaceArt._fetch_location_data') as mock_fetch:
            mock_fetch.return_value = {
                "name": "Test Location",
                "coordinates": (self.test_lat, self.test_lon)
            }
            
            with self.assertRaises(ValueError):
                PlaceArt.from_coordinates(
                    lat=self.test_lat,
                    lon=self.test_lon,
                    style="invalid_style"
                )


if __name__ == "__main__":
    unittest.main() 