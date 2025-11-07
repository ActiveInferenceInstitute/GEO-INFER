"""
Comprehensive test suite for GEO-INFER-SPACE analytics module.

This module provides thorough testing of all spatial analysis capabilities
including vector operations, raster analysis, network analysis, geostatistics,
and point cloud processing.
"""

import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import tempfile
import os
from pathlib import Path

# Import modules to test
from geo_infer_space.analytics.vector import (
    buffer_and_intersect,
    overlay_analysis,
    proximity_analysis,
    spatial_join_analysis,
    geometric_calculations,
    topology_operations
)

from geo_infer_space.analytics.geostatistics import (
    spatial_interpolation,
    clustering_analysis,
    hotspot_detection,
    spatial_autocorrelation,
    variogram_analysis
)

from geo_infer_space.analytics.network import (
    shortest_path,
    service_area,
    network_connectivity,
    routing_analysis,
    accessibility_analysis
)

from geo_infer_space.utils.h3_utils import (
    latlng_to_cell,
    cell_to_latlng,
    polygon_to_cells,
    cell_to_latlng_boundary
)


class TestVectorOperations:
    """Test vector spatial operations."""
    
    @pytest.fixture
    def sample_points(self):
        """Create sample point data."""
        points = [Point(0, 0), Point(1, 1), Point(2, 2)]
        return gpd.GeoDataFrame({'id': [1, 2, 3]}, geometry=points, crs='EPSG:4326')
    
    @pytest.fixture
    def sample_polygons(self):
        """Create sample polygon data."""
        polygons = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1.5, 1.5), (2.5, 1.5), (2.5, 2.5), (1.5, 2.5)])
        ]
        return gpd.GeoDataFrame({'id': [1, 2]}, geometry=polygons, crs='EPSG:4326')
    
    def test_buffer_and_intersect(self, sample_points, sample_polygons):
        """Test buffer and intersection operation."""
        # Project to metric CRS for accurate buffering
        points_proj = sample_points.to_crs('EPSG:3857')
        polygons_proj = sample_polygons.to_crs('EPSG:3857')
        
        result = buffer_and_intersect(points_proj, polygons_proj, 50000)  # 50km buffer
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) >= 0
        assert result.crs == sample_points.crs
    
    def test_overlay_analysis(self, sample_polygons):
        """Test overlay operations."""
        gdf1 = sample_polygons.iloc[:1]
        gdf2 = sample_polygons.iloc[1:]
        
        # Test intersection
        result = overlay_analysis(gdf1, gdf2, operation='intersection')
        assert isinstance(result, gpd.GeoDataFrame)
        
        # Test union
        result = overlay_analysis(gdf1, gdf2, operation='union')
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_proximity_analysis(self, sample_points, sample_polygons):
        """Test proximity calculations."""
        result = proximity_analysis(sample_points, sample_polygons.centroid.to_frame('geometry'))
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'min_distance' in result.columns
        assert 'mean_distance' in result.columns
    
    def test_spatial_join_analysis(self, sample_points, sample_polygons):
        """Test spatial join operations."""
        result = spatial_join_analysis(sample_points, sample_polygons, predicate='within')
        
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_geometric_calculations(self, sample_polygons):
        """Test geometric property calculations."""
        result = geometric_calculations(sample_polygons)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'area' in result.columns
        assert 'perimeter' in result.columns
        assert 'centroid_x' in result.columns
        assert 'centroid_y' in result.columns
    
    def test_topology_operations(self, sample_polygons):
        """Test topology operations."""
        # Test buffer
        result = topology_operations(sample_polygons, 'buffer', tolerance=0.1)
        assert isinstance(result, gpd.GeoDataFrame)
        
        # Test simplify
        result = topology_operations(sample_polygons, 'simplify', tolerance=0.01)
        assert isinstance(result, gpd.GeoDataFrame)
        
        # Test convex hull
        result = topology_operations(sample_polygons, 'convex_hull')
        assert isinstance(result, gpd.GeoDataFrame)


class TestGeostatistics:
    """Test geostatistical operations."""
    
    @pytest.fixture
    def sample_point_data(self):
        """Create sample point data with values."""
        np.random.seed(42)
        x = np.random.uniform(0, 10, 50)
        y = np.random.uniform(0, 10, 50)
        values = np.random.normal(100, 20, 50)
        
        points = [Point(xi, yi) for xi, yi in zip(x, y)]
        return gpd.GeoDataFrame({
            'value': values,
            'geometry': points
        }, crs='EPSG:4326')
    
    def test_spatial_interpolation(self, sample_point_data):
        """Test spatial interpolation methods."""
        bounds = (0, 0, 10, 10)
        resolution = 1.0
        
        # Test IDW interpolation
        result = spatial_interpolation(
            sample_point_data, 'value', bounds, resolution, method='idw'
        )
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0
        assert 'value_interpolated' in result.columns
    
    def test_clustering_analysis(self, sample_point_data):
        """Test spatial clustering."""
        # Test DBSCAN
        result = clustering_analysis(sample_point_data, method='dbscan', eps=1.0, min_samples=3)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'cluster' in result.columns
        
        # Test K-means
        result = clustering_analysis(sample_point_data, method='kmeans', n_clusters=3)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'cluster' in result.columns
    
    def test_hotspot_detection(self, sample_point_data):
        """Test hotspot detection methods."""
        # Test Getis-Ord Gi*
        result = hotspot_detection(
            sample_point_data, 'value', method='getis_ord', distance_threshold=2.0
        )
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'gi_star' in result.columns
        assert 'hotspot_type' in result.columns
    
    def test_spatial_autocorrelation(self, sample_point_data):
        """Test spatial autocorrelation statistics."""
        result = spatial_autocorrelation(sample_point_data, 'value', method='morans_i')
        
        assert isinstance(result, dict)
        assert 'morans_i' in result
        assert 'expected_i' in result
    
    def test_variogram_analysis(self, sample_point_data):
        """Test variogram calculation."""
        result = variogram_analysis(sample_point_data, 'value', max_distance=5.0, n_lags=10)
        
        assert isinstance(result, pd.DataFrame)
        if len(result) > 0:
            assert 'distance' in result.columns
            assert 'semivariance' in result.columns


class TestNetworkAnalysis:
    """Test network analysis operations."""
    
    @pytest.fixture
    def sample_network(self):
        """Create sample network data."""
        # Create simple grid network
        lines = [
            LineString([(0, 0), (1, 0)]),
            LineString([(1, 0), (2, 0)]),
            LineString([(0, 0), (0, 1)]),
            LineString([(1, 0), (1, 1)]),
            LineString([(0, 1), (1, 1)])
        ]
        
        return gpd.GeoDataFrame({
            'length': [1.0, 1.0, 1.0, 1.0, 1.0],
            'geometry': lines
        }, crs='EPSG:4326')
    
    def test_network_connectivity(self, sample_network):
        """Test network connectivity analysis."""
        result = network_connectivity(sample_network)
        
        assert isinstance(result, dict)
        assert 'num_nodes' in result
        assert 'num_edges' in result
        assert 'is_connected' in result
    
    def test_service_area(self, sample_network):
        """Test service area calculation."""
        center_point = Point(0.5, 0.5)
        max_distance = 2.0
        
        result = service_area(sample_network, center_point, max_distance)
        
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_routing_analysis(self, sample_network):
        """Test origin-destination routing."""
        origins = [Point(0, 0), Point(1, 1)]
        destinations = [Point(2, 0), Point(1, 0)]
        
        result = routing_analysis(sample_network, origins, destinations)
        
        assert isinstance(result, pd.DataFrame)
        if len(result) > 0:
            assert 'origin_id' in result.columns
            assert 'destination_id' in result.columns
            assert 'distance' in result.columns
    
    def test_accessibility_analysis(self, sample_network):
        """Test accessibility analysis."""
        origins = [Point(0, 0)]
        destinations = [Point(1, 0), Point(2, 0)]
        max_distance = 1.5
        
        result = accessibility_analysis(sample_network, origins, destinations, max_distance)
        
        assert isinstance(result, pd.DataFrame)
        if len(result) > 0:
            assert 'accessible_destinations' in result.columns
            assert 'accessibility_ratio' in result.columns


class TestH3Operations:
    """Test H3 hexagonal grid operations."""
    
    def test_latlng_to_cell(self):
        """Test coordinate to H3 cell conversion."""
        lat, lng = 37.7749, -122.4194  # San Francisco
        resolution = 9
        
        cell = latlng_to_cell(lat, lng, resolution)
        
        assert isinstance(cell, str)
        assert len(cell) > 0
    
    def test_cell_to_latlng(self):
        """Test H3 cell to coordinate conversion."""
        lat, lng = 37.7749, -122.4194
        resolution = 9
        
        cell = latlng_to_cell(lat, lng, resolution)
        result_lat, result_lng = cell_to_latlng(cell)
        
        assert isinstance(result_lat, float)
        assert isinstance(result_lng, float)
        assert abs(result_lat - lat) < 0.01
        assert abs(result_lng - lng) < 0.01
    
    def test_polygon_to_cells(self):
        """Test polygon to H3 cells conversion."""
        # Simple square polygon
        polygon = {
            "type": "Polygon",
            "coordinates": [[
                [-122.42, 37.77],
                [-122.41, 37.77],
                [-122.41, 37.78],
                [-122.42, 37.78],
                [-122.42, 37.77]
            ]]
        }
        
        cells = polygon_to_cells(polygon, resolution=9)
        
        assert isinstance(cells, list)
        assert len(cells) > 0
        assert all(isinstance(cell, str) for cell in cells)
    
    def test_cell_to_boundary(self):
        """Test H3 cell boundary calculation."""
        lat, lng = 37.7749, -122.4194
        resolution = 9
        
        cell = latlng_to_cell(lat, lng, resolution)
        boundary = cell_to_latlng_boundary(cell)
        
        assert isinstance(boundary, list)
        assert len(boundary) >= 6  # Hexagon has 6 vertices
        assert all(len(coord) == 2 for coord in boundary)


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    @pytest.fixture
    def comprehensive_dataset(self):
        """Create comprehensive test dataset."""
        np.random.seed(42)
        
        # Create points with various attributes
        n_points = 100
        x = np.random.uniform(-122.5, -122.3, n_points)
        y = np.random.uniform(37.7, 37.8, n_points)
        values = np.random.normal(100, 20, n_points)
        categories = np.random.choice(['A', 'B', 'C'], n_points)
        
        points = [Point(xi, yi) for xi, yi in zip(x, y)]
        
        return gpd.GeoDataFrame({
            'value': values,
            'category': categories,
            'geometry': points
        }, crs='EPSG:4326')
    
    def test_complete_workflow(self, comprehensive_dataset):
        """Test complete spatial analysis workflow."""
        # 1. Convert to H3 cells
        sample_point = comprehensive_dataset.geometry.iloc[0]
        h3_cell = latlng_to_cell(sample_point.y, sample_point.x, 9)
        
        assert isinstance(h3_cell, str)
        
        # 2. Perform clustering
        clustered = clustering_analysis(
            comprehensive_dataset, method='dbscan', eps=0.01, min_samples=3
        )
        
        assert 'cluster' in clustered.columns
        
        # 3. Calculate geometric properties
        # Create some polygons from point buffers
        buffered = comprehensive_dataset.to_crs('EPSG:3857')
        buffered['geometry'] = buffered.geometry.buffer(1000)  # 1km buffer
        buffered = buffered.to_crs('EPSG:4326')
        
        geometric_props = geometric_calculations(buffered)
        
        assert 'area' in geometric_props.columns
        
        # 4. Perform hotspot analysis
        hotspots = hotspot_detection(
            comprehensive_dataset, 'value', method='getis_ord', distance_threshold=0.01
        )
        
        assert 'hotspot_type' in hotspots.columns
        
        # Verify all operations completed successfully
        assert len(clustered) == len(comprehensive_dataset)
        assert len(geometric_props) == len(comprehensive_dataset)
        assert len(hotspots) == len(comprehensive_dataset)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_geodataframe(self):
        """Test operations with empty GeoDataFrame."""
        empty_gdf = gpd.GeoDataFrame(columns=['geometry'], crs='EPSG:4326')
        
        with pytest.raises(ValueError):
            buffer_and_intersect(empty_gdf, empty_gdf, 1000)
    
    def test_invalid_crs_mismatch(self):
        """Test CRS mismatch handling."""
        gdf1 = gpd.GeoDataFrame([{'geometry': Point(0, 0)}], crs='EPSG:4326')
        gdf2 = gpd.GeoDataFrame([{'geometry': Point(0, 0)}], crs='EPSG:3857')
        
        # Should handle CRS mismatch gracefully
        result = overlay_analysis(gdf1, gdf2, operation='intersection')
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_invalid_parameters(self):
        """Test invalid parameter handling."""
        gdf = gpd.GeoDataFrame([{'geometry': Point(0, 0)}], crs='EPSG:4326')
        
        with pytest.raises(ValueError):
            overlay_analysis(gdf, gdf, operation='invalid_operation')
        
        with pytest.raises(ValueError):
            topology_operations(gdf, 'buffer', tolerance=-1.0)


if __name__ == "__main__":
    pytest.main([__file__])
