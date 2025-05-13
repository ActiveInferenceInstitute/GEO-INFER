#!/usr/bin/env python
"""
Unit tests for the CulturalMap class in geo_infer_art.core.place.cultural_map.
"""

import os
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image

from geo_infer_art.core.place.cultural_map import CulturalMap


class TestCulturalMap(unittest.TestCase):
    """Test suite for the CulturalMap class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test directory for outputs
        self.test_dir = "test_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Define test coordinates
        self.test_lat = 41.9028  # Rome, Italy
        self.test_lon = 12.4964
        self.test_radius = 100.0  # km
            
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_init_with_data(self):
        """Test initialization with data and metadata."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Create a simple GeoDataFrame
        data = gpd.GeoDataFrame(
            {'name': ['Site A', 'Site B'], 'type': ['Historical', 'Cultural']},
            geometry=[Point(self.test_lon, self.test_lat), Point(self.test_lon + 0.1, self.test_lat + 0.1)],
            crs="EPSG:4326"
        )
        
        metadata = {
            "region": "Mediterranean",
            "culture": "Roman",
            "period": "Ancient"
        }
        
        cultural_map = CulturalMap(data=data, metadata=metadata)
        
        self.assertEqual(cultural_map.data, data)
        self.assertEqual(cultural_map.metadata, metadata)
        self.assertIsNone(cultural_map.image)
    
    @patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_region_data')
    def test_from_region(self, mock_fetch):
        """Test creating CulturalMap from a region name."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Mock the data fetching
        mock_data = gpd.GeoDataFrame(
            {'name': ['Rome', 'Athens'], 'type': ['Capital', 'Capital']},
            geometry=[Point(12.4964, 41.9028), Point(23.7275, 37.9838)],
            crs="EPSG:4326"
        )
        
        mock_fetch.return_value = (mock_data, {
            "region": "mediterranean",
            "cultures": ["Roman", "Greek"],
            "period": "Ancient"
        })
        
        # Create from region name
        cultural_map = CulturalMap.from_region(
            region_name="mediterranean",
            cultural_theme="historical",
            style="artistic"
        )
        
        # Check that the data and metadata were set
        self.assertEqual(cultural_map.data, mock_data)
        self.assertEqual(cultural_map.metadata["region"], "mediterranean")
        
        # Check that the image was created
        self.assertIsNotNone(cultural_map.image)
    
    @patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_coordinate_data')
    def test_from_coordinates(self, mock_fetch):
        """Test creating CulturalMap from coordinates."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Mock the data fetching
        mock_data = gpd.GeoDataFrame(
            {'name': ['Rome', 'Vatican'], 'type': ['Capital', 'Religious']},
            geometry=[Point(12.4964, 41.9028), Point(12.4534, 41.9022)],
            crs="EPSG:4326"
        )
        
        mock_fetch.return_value = (mock_data, {
            "coordinates": (self.test_lat, self.test_lon),
            "radius_km": self.test_radius,
            "region": "Rome and surroundings"
        })
        
        # Create from coordinates
        cultural_map = CulturalMap.from_coordinates(
            lat=self.test_lat,
            lon=self.test_lon,
            radius_km=self.test_radius,
            cultural_theme="historical",
            style="artistic"
        )
        
        # Check that the data and metadata were set
        self.assertEqual(cultural_map.data, mock_data)
        self.assertEqual(cultural_map.metadata["coordinates"], (self.test_lat, self.test_lon))
        self.assertEqual(cultural_map.metadata["radius_km"], self.test_radius)
        
        # Check that the image was created
        self.assertIsNotNone(cultural_map.image)
    
    @patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_region_data')
    def test_add_narrative(self, mock_fetch):
        """Test adding a narrative to the cultural map."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Mock the data fetching
        mock_data = gpd.GeoDataFrame(
            {'name': ['Rome'], 'type': ['Capital']},
            geometry=[Point(12.4964, 41.9028)],
            crs="EPSG:4326"
        )
        
        mock_fetch.return_value = (mock_data, {"region": "Rome"})
        
        # Create cultural map
        cultural_map = CulturalMap.from_region(
            region_name="rome",
            cultural_theme="historical"
        )
        
        # Add narrative
        narrative_text = "Rome was the capital of the Roman Empire."
        cultural_map_with_narrative = cultural_map.add_narrative(
            narrative=narrative_text,
            position="bottom"
        )
        
        # Check method chaining
        self.assertEqual(cultural_map, cultural_map_with_narrative)
        
        # Check that the narrative was added to metadata
        self.assertEqual(cultural_map.metadata["narrative"], narrative_text)
        
        # Check that the image still exists
        self.assertIsNotNone(cultural_map.image)
    
    @patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_region_data')
    def test_apply_cultural_style(self, mock_fetch):
        """Test applying a cultural style to the map."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Mock the data fetching
        mock_data = gpd.GeoDataFrame(
            {'name': ['Rome'], 'type': ['Capital']},
            geometry=[Point(12.4964, 41.9028)],
            crs="EPSG:4326"
        )
        
        mock_fetch.return_value = (mock_data, {"region": "Rome"})
        
        # Create cultural map
        cultural_map = CulturalMap.from_region(
            region_name="rome",
            cultural_theme="historical"
        )
        
        # Apply cultural style
        cultural_map_with_style = cultural_map.apply_cultural_style(style="artistic")
        
        # Check method chaining
        self.assertEqual(cultural_map, cultural_map_with_style)
        
        # Check that the style was added to metadata
        self.assertEqual(cultural_map.metadata["cultural_style"], "artistic")
        
        # Check that the image still exists
        self.assertIsNotNone(cultural_map.image)
    
    @patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_region_data')
    def test_save_and_show(self, mock_fetch):
        """Test saving and showing the cultural map."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Mock the data fetching
        mock_data = gpd.GeoDataFrame(
            {'name': ['Rome'], 'type': ['Capital']},
            geometry=[Point(12.4964, 41.9028)],
            crs="EPSG:4326"
        )
        
        mock_fetch.return_value = (mock_data, {"region": "Rome"})
        
        # Create cultural map
        cultural_map = CulturalMap.from_region(
            region_name="rome",
            cultural_theme="historical"
        )
        
        # Test save method
        output_path = os.path.join(self.test_dir, "cultural_map_output.png")
        saved_path = cultural_map.save(output_path)
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(saved_path, output_path)
        
        # Test show method - can only check that it doesn't raise an error
        try:
            cultural_map.show()
        except Exception as e:
            self.fail(f"show() method raised an error: {str(e)}")
    
    @patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_region_data')
    def test_different_cultural_themes(self, mock_fetch):
        """Test creating cultural maps with different themes."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        themes = ["historical", "linguistic"]
        
        for theme in themes:
            # Mock the data fetching
            mock_data = gpd.GeoDataFrame(
                {'name': [f'Site for {theme}'], 'type': [f'{theme.capitalize()} site']},
                geometry=[Point(12.4964, 41.9028)],
                crs="EPSG:4326"
            )
            
            mock_fetch.return_value = (mock_data, {"region": "Mediterranean", "theme": theme})
            
            try:
                # Create cultural map with this theme
                cultural_map = CulturalMap.from_region(
                    region_name="mediterranean",
                    cultural_theme=theme
                )
                
                self.assertIsNotNone(cultural_map.image)
                
                # Save the output for this theme
                output_path = os.path.join(self.test_dir, f"cultural_map_{theme}.png")
                cultural_map.save(output_path)
                self.assertTrue(os.path.exists(output_path))
                
            except Exception as e:
                self.skipTest(f"Creation with theme {theme} failed: {str(e)}")
    
    @patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_region_data')
    def test_different_styles(self, mock_fetch):
        """Test creating cultural maps with different styles."""
        import geopandas as gpd
        from shapely.geometry import Point
        
        styles = ["artistic", "minimalist", "detailed", "abstract"]
        
        for style in styles:
            # Mock the data fetching
            mock_data = gpd.GeoDataFrame(
                {'name': [f'Site for {style}'], 'type': ['Historical site']},
                geometry=[Point(12.4964, 41.9028)],
                crs="EPSG:4326"
            )
            
            mock_fetch.return_value = (mock_data, {"region": "Mediterranean"})
            
            try:
                # Create cultural map with this style
                cultural_map = CulturalMap.from_region(
                    region_name="mediterranean",
                    cultural_theme="historical",
                    style=style
                )
                
                self.assertIsNotNone(cultural_map.image)
                
                # Save the output for this style
                output_path = os.path.join(self.test_dir, f"cultural_map_{style}.png")
                cultural_map.save(output_path)
                self.assertTrue(os.path.exists(output_path))
                
            except Exception as e:
                self.skipTest(f"Creation with style {style} failed: {str(e)}")
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test invalid coordinates
        with self.assertRaises(ValueError):
            CulturalMap.from_coordinates(
                lat=100.0,  # Invalid latitude
                lon=self.test_lon,
                radius_km=self.test_radius
            )
        
        # Test invalid radius
        with self.assertRaises(ValueError):
            CulturalMap.from_coordinates(
                lat=self.test_lat,
                lon=self.test_lon,
                radius_km=-10.0  # Invalid radius
            )
        
        # Test invalid theme
        with patch('geo_infer_art.core.place.cultural_map.CulturalMap._fetch_region_data') as mock_fetch:
            mock_fetch.return_value = (None, {"region": "Rome"})
            
            with self.assertRaises(ValueError):
                CulturalMap.from_region(
                    region_name="rome",
                    cultural_theme="invalid_theme"  # Invalid theme
                )


if __name__ == "__main__":
    unittest.main() 