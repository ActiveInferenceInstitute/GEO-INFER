import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from geo_infer_space.core.spatial_processor import SpatialProcessor

@pytest.fixture
def sample_processor():
    return SpatialProcessor()

def test_buffer_analysis(sample_processor):
    """Test buffer creation with real points."""
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1)])
    buffered = sample_processor.buffer_analysis(gdf, 1.0)
    assert len(buffered) == 2
    assert all(buffered.geometry.area > 0)

def test_proximity_analysis(sample_processor):
    """Test proximity calculation with real geometries."""
    gdf1 = gpd.GeoDataFrame(geometry=[Point(0, 0)])
    gdf2 = gpd.GeoDataFrame(geometry=[Point(1, 1), Point(2, 2)])
    result = sample_processor.proximity_analysis(gdf1, gdf2)
    assert 'min_distance' in result
    assert result['min_distance'] > 0

def test_buffer_analysis_empty():
    """Test buffer with empty input."""
    processor = SpatialProcessor()
    empty_gdf = gpd.GeoDataFrame(geometry=[])
    with pytest.raises(ValueError):
        processor.buffer_analysis(empty_gdf, 1.0) 