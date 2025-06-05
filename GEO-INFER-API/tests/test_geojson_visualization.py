"""
Tests for GeoJSON visualization capabilities.

This file tests the ability to export GeoJSON data to formats 
that can be used for visualization.
"""
import json
import pytest
import os
from tempfile import NamedTemporaryFile

from geo_infer_api.models.geojson import (
    GeoJSONType, Polygon, PolygonFeature, PolygonFeatureCollection
)


# Test data
SAMPLE_POLYGONS = [
    {
        "id": "sf-triangle",
        "name": "San Francisco Triangle",
        "coordinates": [
            [
                [-122.51, 37.77],
                [-122.42, 37.81],
                [-122.37, 37.73],
                [-122.51, 37.77]
            ]
        ]
    },
    {
        "id": "nyc-square",
        "name": "New York Square",
        "coordinates": [
            [
                [-74.01, 40.70],
                [-73.96, 40.70],
                [-73.96, 40.75],
                [-74.01, 40.75],
                [-74.01, 40.70]
            ]
        ]
    }
]


def create_feature_collection():
    """Create a sample PolygonFeatureCollection for testing."""
    features = []
    
    for poly in SAMPLE_POLYGONS:
        polygon = Polygon(type=GeoJSONType.POLYGON, coordinates=poly["coordinates"])
        feature = PolygonFeature(
            type=GeoJSONType.FEATURE,
            id=poly["id"],
            geometry=polygon,
            properties={"name": poly["name"]}
        )
        features.append(feature)
    
    return PolygonFeatureCollection(
        type=GeoJSONType.FEATURE_COLLECTION,
        features=features
    )


def test_feature_collection_to_geojson():
    """Test conversion of PolygonFeatureCollection to GeoJSON string."""
    fc = create_feature_collection()
    
    # Convert to GeoJSON string
    geojson_str = fc.json(exclude_none=True)
    
    # Parse the JSON string to make sure it's valid
    geojson_data = json.loads(geojson_str)
    
    # Verify structure
    assert geojson_data["type"] == "FeatureCollection"
    assert len(geojson_data["features"]) == 2
    assert geojson_data["features"][0]["id"] == "sf-triangle"
    assert geojson_data["features"][1]["id"] == "nyc-square"


def test_feature_collection_to_file():
    """Test writing PolygonFeatureCollection to a GeoJSON file."""
    fc = create_feature_collection()
    
    # Create a temporary file
    with NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
        tmp_path = tmp.name
        # Write GeoJSON to the file
        tmp.write(fc.json(exclude_none=True).encode('utf-8'))
    
    try:
        # Verify file exists and has content
        assert os.path.exists(tmp_path)
        assert os.path.getsize(tmp_path) > 0
        
        # Read the file and verify content
        with open(tmp_path, 'r') as f:
            geojson_data = json.load(f)
        
        assert geojson_data["type"] == "FeatureCollection"
        assert len(geojson_data["features"]) == 2
        assert geojson_data["features"][0]["id"] == "sf-triangle"
        assert geojson_data["features"][1]["id"] == "nyc-square"
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_feature_dict_conversion():
    """Test conversion between PolygonFeature and dictionary."""
    # Create a feature
    polygon = Polygon(type=GeoJSONType.POLYGON, coordinates=SAMPLE_POLYGONS[0]["coordinates"])
    feature = PolygonFeature(
        type=GeoJSONType.FEATURE,
        id=SAMPLE_POLYGONS[0]["id"],
        geometry=polygon,
        properties={"name": SAMPLE_POLYGONS[0]["name"]}
    )
    
    # Convert to dict
    feature_dict = feature.dict(exclude_none=True)
    
    # Verify dict structure
    assert feature_dict["type"] == "Feature"
    assert feature_dict["id"] == "sf-triangle"
    assert feature_dict["geometry"]["type"] == "Polygon"
    
    # Check coordinates structure - note that the internal representation uses tuples instead of lists
    # so we need to check the structure and values separately
    coords_from_dict = feature_dict["geometry"]["coordinates"]
    coords_from_sample = SAMPLE_POLYGONS[0]["coordinates"]
    
    # Verify the structures match
    assert len(coords_from_dict) == len(coords_from_sample)
    assert len(coords_from_dict[0]) == len(coords_from_sample[0])
    
    # Verify the actual coordinate values
    for i in range(len(coords_from_dict)):
        for j in range(len(coords_from_dict[i])):
            # In dict, the coordinates are tuples, but in sample, they are lists
            assert coords_from_dict[i][j][0] == coords_from_sample[i][j][0]  # longitude
            assert coords_from_dict[i][j][1] == coords_from_sample[i][j][1]  # latitude
    
    assert feature_dict["properties"]["name"] == "San Francisco Triangle"
    
    # Create a new feature from the dict
    new_feature = PolygonFeature(**feature_dict)
    
    # Verify it matches the original
    assert new_feature.type == feature.type
    assert new_feature.id == feature.id
    assert new_feature.geometry.type == feature.geometry.type
    
    # Again, compare coordinates manually
    for i in range(len(new_feature.geometry.coordinates)):
        for j in range(len(new_feature.geometry.coordinates[i])):
            assert new_feature.geometry.coordinates[i][j][0] == feature.geometry.coordinates[i][j][0]
            assert new_feature.geometry.coordinates[i][j][1] == feature.geometry.coordinates[i][j][1]
    
    assert new_feature.properties == feature.properties 