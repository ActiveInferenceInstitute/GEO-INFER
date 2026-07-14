import pytest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from geo_infer_space.spatial_utils import SpatialUtils

@pytest.fixture
def spatial_utils():
    return SpatialUtils()

def test_transform_coordinates(spatial_utils):
    """Behavior-focused test: test_transform_coordinates."""
    # Single tuple
    result = spatial_utils.transform_coordinates((37.7749, -122.4194), "EPSG:4326", "EPSG:3857")
    assert isinstance(result, tuple)
    assert len(result) == 2

    # List of tuples
    coords = [(37.7749, -122.4194), (34.0522, -118.2437)]
    results = spatial_utils.transform_coordinates(coords, "EPSG:4326", "EPSG:3857")
    assert isinstance(results, list)
    assert len(results) == 2
    assert isinstance(results[0], tuple)

    # Empty
    assert spatial_utils.transform_coordinates([]) == []

def test_calculate_distance(spatial_utils):
    """Behavior-focused test: test_calculate_distance."""
    sf = (37.7749, -122.4194)
    la = (34.0522, -118.2437)
    dist = spatial_utils.calculate_distance(sf, la, method="haversine")
    assert 500 < dist < 600

    dist_euclid = spatial_utils.calculate_distance(sf, la, method="euclidean")
    assert dist_euclid > 0

    with pytest.raises(ValueError):
       spatial_utils.calculate_distance(sf, la, method="unknown")

def test_find_nearest_point(spatial_utils):
    """Behavior-focused test: test_find_nearest_point."""
    target = (37.7749, -122.4194)
    candidates = [(34.0522, -118.2437), (37.8044, -122.2712), (40.7128, -74.0060)]
    
    idx, dist = spatial_utils.find_nearest_point(target, candidates)
    # Oakland is nearest to SF
    assert idx == 1
    assert dist < 50
    
    with pytest.raises(ValueError):
       spatial_utils.find_nearest_point(target, [])

def test_create_spatial_index(spatial_utils):
    """Behavior-focused test: test_create_spatial_index."""
    points = [(37.7749, -122.4194), (34.0522, -118.2437)]
    index_data = spatial_utils.create_spatial_index(points)
    
    assert 'bounds' in index_data
    assert 'centroid' in index_data
    assert 'sindex' in index_data
    assert len(index_data['labels']) == 2
    
def test_filter_points_by_distance(spatial_utils):
    """Behavior-focused test: test_filter_points_by_distance."""
    center = (37.7749, -122.4194)
    p1 = (37.8044, -122.2712) # Close
    p2 = (40.7128, -74.0060) # Far
    
    filtered = spatial_utils.filter_points_by_distance(center, [p1, p2], max_distance_km=100)
    assert len(filtered) == 1
    assert filtered[0] == p1
