#!/usr/bin/env python3
"""
Tests for PlaceAnalyzer
"""
import pytest
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
from geo_infer_space.core.place_analyzer import PlaceAnalyzer
from geo_infer_space.core.spatial_processor import SpatialProcessor

class TestPlaceAnalyzer:
    @pytest.fixture
    def analyzer(self, tmp_path):
        base_dir = tmp_path / 'test_dir'
        base_dir.mkdir(exist_ok=True)
        return PlaceAnalyzer('TestPlace', base_dir)
    
    def test_init(self, analyzer):
        assert analyzer.place_name == 'TestPlace'
        assert analyzer.base_dir.name == 'test_dir'  # Adjusted for tmp_path
    
    def test_load_place_data(self, analyzer):
        # Create sample data
        sample_gdf = gpd.GeoDataFrame({'geometry': [Point(0, 0)]}, crs='EPSG:4326')
        data_path = analyzer.data_dir / 'sample.geojson'
        sample_gdf.to_file(data_path, driver='GeoJSON')
        
        loaded_data = analyzer.load_place_data('sample.geojson')
        assert isinstance(loaded_data, gpd.GeoDataFrame)
        assert len(loaded_data) == 1
        assert loaded_data.crs == 'EPSG:4326'

    def test_analyze_place(self, analyzer):
        # Create sample data
        sample_gdf = gpd.GeoDataFrame({'geometry': [Point(0, 0), Point(1, 1)]}, crs='EPSG:4326')
        data_path = analyzer.data_dir / 'analyze_sample.geojson'
        sample_gdf.to_file(data_path, driver='GeoJSON')
        
        analyzer.load_place_data('analyze_sample.geojson')
        result = analyzer.analyze_place()
        assert isinstance(result, dict)
        assert 'num_features' in result
        assert result['num_features'] == 2

    def test_buffer_analysis_integration(self, analyzer):
        sample_gdf = gpd.GeoDataFrame({'geometry': [Point(0, 0)]}, crs='EPSG:4326')
        buffered = analyzer.spatial_processor.buffer_analysis(sample_gdf, 1000)
        assert isinstance(buffered, gpd.GeoDataFrame)
        assert buffered.geometry.area.iloc[0] > 0 