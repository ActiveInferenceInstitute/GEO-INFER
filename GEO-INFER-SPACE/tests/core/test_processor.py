import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from geo_infer_space.core.processor import SpatialProcessor

import h3
import numpy as np

def test_buffer_analysis():
    """Test basic buffer analysis."""
    processor = SpatialProcessor()
    
    # Create sample data
    points = [Point(0, 0), Point(1, 1)]
    gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
    
    buffered = processor.buffer_analysis(gdf, buffer_distance=1.0)
    
    assert len(buffered) == len(gdf)
    assert all(buffered.geometry.type == 'Polygon')
    
@pytest.mark.parametrize("dissolve, expected_type", [
    (False, 'Polygon'),
    (True, 'Polygon')
])
def test_buffer_dissolve(dissolve, expected_type):
    """Test buffer with dissolve option."""
    processor = SpatialProcessor()
    points = [Point(0, 0), Point(0.5, 0.5)]
    gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
    
    buffered = processor.buffer_analysis(gdf, 100000.0, dissolve=dissolve)
    
    if dissolve:
        assert isinstance(buffered.geometry, gpd.GeoSeries)
        assert len(buffered) == 1
        assert buffered.geometry.iloc[0].geom_type == expected_type
    else:
        assert len(buffered) == 2
        assert all(buffered.geometry.geom_type == expected_type) 

def test_proximity_analysis():
    """Test proximity analysis with buffer and intersect."""
    processor = SpatialProcessor()
    
    # Sample points
    points = [Point(0, 0)]
    points_gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
    
    # Sample polygons
    polygon = Polygon([( -1, -1), (1, -1), (1, 1), (-1, 1)])
    polygons_gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
    
    result = processor.proximity_analysis(points_gdf, polygons_gdf, 100000.0)
    
    assert not result.empty
    assert 'geometry' in result.columns
    assert result.geometry.iloc[0].geom_type == 'Polygon' 

def test_h3_to_coordinates():
    """Test getting center coordinates of an H3 cell."""
    processor = SpatialProcessor()
    lat, lon = processor.h3_to_coordinates("88283082bfffffff")
    assert isinstance(lat, float)
    assert isinstance(lon, float)
    assert abs(lat - 40.659) < 0.1  # Approximate check for known cell
    assert abs(lon - -112.826) < 0.1

def test_create_h3_grid():
    """Test generating H3 grid over bounds."""
    processor = SpatialProcessor()
    bounds = (-124.4, 41.5, -123.5, 42.0)
    grid = processor.create_h3_grid(bounds, resolution=5)
    assert isinstance(grid, list)
    assert len(grid) > 0
    assert all(h3.is_valid_cell(cell) for cell in grid)

def test_perform_multi_overlay():
    """Test multi-layer spatial overlay."""
    processor = SpatialProcessor()
    
    # Sample data
    gdf1 = gpd.GeoDataFrame({
        'geometry': [Polygon([(0,0), (2,0), (2,2), (0,2)])],
        'value1': [1]
    }, crs="EPSG:4326")
    
    gdf2 = gpd.GeoDataFrame({
        'geometry': [Polygon([(1,1), (3,1), (3,3), (1,3)])],
        'value2': [2]
    }, crs="EPSG:4326")
    
    datasets = {'layer1': gdf1, 'layer2': gdf2}
    result = processor.perform_multi_overlay(datasets)
    
    assert isinstance(result, gpd.GeoDataFrame)
    assert not result.empty
    assert 'domain' in result.columns
    assert len(result) >= 2  # At least intersection and differences

def test_calculate_spatial_correlation():
    """Test spatial correlation calculation."""
    processor = SpatialProcessor()
    
    map1 = {
        'cell1': 0.5,
        'cell2': 0.6,
        'cell3': 0.7
    }
    map2 = {
        'cell1': 0.4,
        'cell2': 0.65,
        'cell3': 0.8
    }
    
    corr = processor.calculate_spatial_correlation(map1, map2)
    assert isinstance(corr, float)
    assert 0 < corr <= 1.0  # Should be positive correlation 