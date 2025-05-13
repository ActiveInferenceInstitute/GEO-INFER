"""Unit tests for geospatial utilities."""

import pytest
import math
import sys
import os
from pathlib import Path

# Add parent directory to the path to find our utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tests.utils.geospatial import (
    create_point, create_polygon, create_feature, create_feature_collection, 
    is_valid_geojson, haversine_distance
)

@pytest.mark.unit
@pytest.mark.geospatial
class TestGeospatialUtils:
    """Test suite for geospatial utilities."""
    
    def test_create_point(self):
        """Test creating a GeoJSON Point."""
        point = create_point(100.0, 0.0)
        
        assert point["type"] == "Point"
        assert point["coordinates"] == [100.0, 0.0]
        assert is_valid_geojson(point)
    
    def test_create_polygon(self):
        """Test creating a GeoJSON Polygon."""
        coords = [
            [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0]
        ]
        polygon = create_polygon(coords)
        
        assert polygon["type"] == "Polygon"
        assert polygon["coordinates"][0][0] == coords[0]
        assert polygon["coordinates"][0][-1] == coords[0]  # Should be closed
        assert len(polygon["coordinates"][0]) == len(coords) + 1  # +1 for closure
        assert is_valid_geojson(polygon)
    
    def test_create_feature(self):
        """Test creating a GeoJSON Feature."""
        point = create_point(100.0, 0.0)
        properties = {"name": "Test Point", "value": 42}
        feature = create_feature(point, properties)
        
        assert feature["type"] == "Feature"
        assert feature["geometry"] == point
        assert feature["properties"] == properties
        assert is_valid_geojson(feature)
    
    def test_create_feature_collection(self):
        """Test creating a GeoJSON FeatureCollection."""
        point_feature = create_feature(create_point(100.0, 0.0), {"name": "Point"})
        polygon_coords = [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0]]
        polygon_feature = create_feature(create_polygon(polygon_coords), {"name": "Polygon"})
        
        fc = create_feature_collection([point_feature, polygon_feature])
        
        assert fc["type"] == "FeatureCollection"
        assert len(fc["features"]) == 2
        assert fc["features"][0] == point_feature
        assert fc["features"][1] == polygon_feature
        assert is_valid_geojson(fc)
    
    def test_haversine_distance(self):
        """Test calculating haversine distance."""
        # San Francisco
        sf_lon, sf_lat = -122.4194, 37.7749
        # Los Angeles
        la_lon, la_lat = -118.2437, 34.0522
        
        # Approximate distance between SF and LA is ~560 km
        distance = haversine_distance(sf_lon, sf_lat, la_lon, la_lat)
        
        assert 550 <= distance <= 570
        
    def test_is_valid_geojson(self):
        """Test geojson validation."""
        # Valid Point
        assert is_valid_geojson({"type": "Point", "coordinates": [0, 0]})
        
        # Valid Feature
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": {"name": "Test"}
        }
        assert is_valid_geojson(feature)
        
        # Invalid - missing type
        assert not is_valid_geojson({"coordinates": [0, 0]})
        
        # Invalid - Feature missing geometry
        invalid_feature = {
            "type": "Feature",
            "properties": {"name": "Test"}
        }
        assert not is_valid_geojson(invalid_feature)
        
        # Invalid - Feature missing properties
        invalid_feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
        }
        assert not is_valid_geojson(invalid_feature) 