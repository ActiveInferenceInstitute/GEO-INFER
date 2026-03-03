import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from geo_infer_space.core.spatial_processor import SpatialProcessor

@pytest.fixture
def sample_processor():
    return SpatialProcessor()

@pytest.mark.spatial
def test_buffer_analysis(sample_processor):
    """Test buffer creation with real points."""
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1)])
    buffered = sample_processor.buffer_analysis(gdf, 1.0)
    assert len(buffered) == 2
    assert all(buffered.geometry.area > 0)

@pytest.mark.spatial
def test_proximity_analysis(sample_processor):
    """Test proximity calculation with real geometries."""
    gdf1 = gpd.GeoDataFrame(geometry=[Point(0, 0)])
    gdf2 = gpd.GeoDataFrame(geometry=[Point(1, 1), Point(2, 2)])
    result = sample_processor.proximity_analysis(gdf1, gdf2)
    assert 'min_distance' in result
    assert result['min_distance'] > 0

@pytest.mark.spatial
def test_buffer_analysis_empty():
    """Test buffer with empty input."""
    processor = SpatialProcessor()
    empty_gdf = gpd.GeoDataFrame(geometry=[])
    with pytest.raises(ValueError):
        processor.buffer_analysis(empty_gdf, 1.0)

@pytest.mark.spatial
def test_proximity_analysis_empty(sample_processor):
    """Test proximity with empty."""
    gdf1 = gpd.GeoDataFrame(geometry=[])
    gdf2 = gpd.GeoDataFrame(geometry=[Point(1, 1)])
    with pytest.raises(ValueError):
        sample_processor.proximity_analysis(gdf1, gdf2)

@pytest.mark.spatial
def test_perform_multi_overlay(sample_processor):
    """Test multi overlay."""
    gdf1 = gpd.GeoDataFrame(geometry=[Point(0, 0)])
    gdf2 = gpd.GeoDataFrame(geometry=[Point(1, 1)])
    datasets = {'A': gdf1, 'B': gdf2}
    result = sample_processor.perform_multi_overlay(datasets)
    assert len(result) == 2
    assert 'domain' in result.columns

@pytest.mark.spatial
def test_calculate_spatial_correlation(sample_processor):
    """Test spatial correlation."""
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1), Point(2, 2)])
    result = sample_processor.calculate_spatial_correlation(gdf)
    assert 'spatial_correlation' in result
    assert result['spatial_correlation'] > 0
    
    # 1 point should return 0.0
    empty_result = sample_processor.calculate_spatial_correlation(gpd.GeoDataFrame(geometry=[Point(0, 0)]))
    assert empty_result['spatial_correlation'] == 0.0 