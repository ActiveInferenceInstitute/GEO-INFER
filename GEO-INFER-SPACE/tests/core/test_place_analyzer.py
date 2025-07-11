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
import pandas as pd
import json

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
        # Create sample GeoJSON
        sample_path = analyzer.data_dir / 'sample.geojson'
        with open(sample_path, 'w') as f:
            json.dump({
                "type": "FeatureCollection",
                "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}, "properties": {}}]
            }, f)
        analyzer.load_place_data([{'name': 'sample', 'path': str(sample_path)}])
        assert len(analyzer.integrated_data) == 1

    def test_analyze_place(self, analyzer):
        # Create sample data
        sample_gdf = gpd.GeoDataFrame({'geometry': [Point(0, 0), Point(1, 1)]}, crs='EPSG:4326')
        data_path = analyzer.data_dir / 'analyze_sample.csv'
        df = pd.DataFrame({'geometry': sample_gdf.geometry.to_wkt()})
        df.to_csv(data_path, index=False)
        analyzer.load_place_data([{'name': 'analyze_sample', 'path': str(data_path)}])
        analyzer.perform_spatial_analysis(['buffer'])
        assert isinstance(analyzer.analysis_results, dict)
        assert 'buffer' in analyzer.analysis_results
        assert len(analyzer.analysis_results['buffer']) == 2

    def test_buffer_analysis_integration(self, analyzer):
        sample_gdf = gpd.GeoDataFrame({'geometry': [Point(0, 0)]}, crs='EPSG:4326')
        buffered = analyzer.processor.buffer_analysis(sample_gdf, 1000)
        assert isinstance(buffered, gpd.GeoDataFrame)
        assert buffered.geometry.area.iloc[0] > 0 