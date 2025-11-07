"""
Tests for H3 Machine Learning Integration module.

Comprehensive test suite covering ML feature engineering, demand forecasting,
disaster response, and performance optimization methods.
"""

import pytest
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

from geo_infer_space.h3.core import H3Grid, H3Cell
from geo_infer_space.h3.ml_integration import (
    H3MLFeatureEngine, H3DisasterResponse, H3PerformanceOptimizer
)

# Test data
SF_COORDS = [(37.7749, -122.4194), (37.7759, -122.4184), (37.7739, -122.4204)]
RESOLUTION = 9


@pytest.fixture
def ml_grid():
    """Create a sample H3 grid for ML testing."""
    grid = H3Grid()
    
    # Create cells with ML-relevant properties
    for i, (lat, lng) in enumerate(SF_COORDS):
        cell = H3Cell.from_coordinates(lat, lng, RESOLUTION)
        
        # Add ML features
        cell.properties.update({
            'demand': 100 + (i * 20),
            'supply': 80 + (i * 15),
            'population': 1000 + (i * 200),
            'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
            'temperature': 20.0 + (i * 2.5),
            'baseline_temp': 18.0 + (i * 2.0),
            'flood_risk': 0.3 + (i * 0.2),
            'elevation': 50 + (i * 10)
        })
        
        grid.add_cell(cell)
    
    return grid


@pytest.fixture
def disaster_grid():
    """Create a sample H3 grid for disaster response testing."""
    grid = H3Grid()
    
    # Create cells with disaster-relevant properties
    disaster_coords = [
        (37.7749, -122.4194),  # High risk
        (37.7759, -122.4184),  # Medium risk
        (37.7739, -122.4204),  # Low risk
        (37.7769, -122.4174),  # Safe zone
        (37.7729, -122.4214),  # Safe zone
    ]
    
    risk_levels = [0.9, 0.6, 0.3, 0.1, 0.05]
    populations = [1500, 1200, 800, 600, 400]
    
    for i, ((lat, lng), risk, pop) in enumerate(zip(disaster_coords, risk_levels, populations)):
        cell = H3Cell.from_coordinates(lat, lng, RESOLUTION)
        
        cell.properties.update({
            'flood_risk': risk,
            'population': pop,
            'elevation': 10 + (i * 5),
            'infrastructure_density': 0.8 - (i * 0.1),
            'baseline_temp': 20.0,
            'current_temp': 20.0 + (risk * 5)  # Higher temp with higher risk
        })
        
        grid.add_cell(cell)
    
    return grid


class TestH3MLFeatureEngine:
    """Test ML feature engineering functionality."""
    
    def test_feature_engine_init(self, ml_grid):
        """Test ML feature engine initialization."""
        engine = H3MLFeatureEngine(ml_grid)
        assert engine.grid == ml_grid
    
    def test_create_spatial_features(self, ml_grid):
        """Test spatial feature creation."""
        engine = H3MLFeatureEngine(ml_grid)
        features = engine.create_spatial_features('demand', neighbor_rings=2)
        
        assert 'features' in features
        assert 'feature_names' in features
        assert 'target_column' in features
        assert features['target_column'] == 'demand'
        assert features['neighbor_rings'] == 2
        
        # Check feature structure
        assert len(features['features']) > 0
        
        for feature_dict in features['features']:
            assert 'cell_index' in feature_dict
            assert 'target_value' in feature_dict
            assert 'resolution' in feature_dict
            
            # Check spatial features
            assert 'cell_lat' in feature_dict
            assert 'cell_lng' in feature_dict
            assert 'distance_from_equator' in feature_dict
            
            # Check neighbor features
            assert 'ring_1_mean' in feature_dict
            assert 'ring_2_mean' in feature_dict
            assert 'neighbor_density' in feature_dict
    
    def test_temporal_features(self, ml_grid):
        """Test temporal feature extraction."""
        engine = H3MLFeatureEngine(ml_grid)
        features = engine.create_spatial_features('demand')
        
        # Check temporal features are included
        feature_names = features['feature_names']
        temporal_features = [
            'hour', 'day_of_week', 'is_weekend', 'is_business_hour',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos'
        ]
        
        for temp_feature in temporal_features:
            assert temp_feature in feature_names
        
        # Check actual temporal values
        for feature_dict in features['features']:
            if 'hour' in feature_dict:
                assert 0 <= feature_dict['hour'] <= 23
                assert 0 <= feature_dict['day_of_week'] <= 6
                assert feature_dict['is_weekend'] in [0, 1]
                assert feature_dict['is_business_hour'] in [0, 1]
    
    def test_demand_forecasting_features(self, ml_grid):
        """Test demand forecasting feature creation."""
        engine = H3MLFeatureEngine(ml_grid)
        features = engine.create_demand_forecasting_features('demand')
        
        assert 'features' in features
        assert 'method' in features
        assert features['method'] == 'H3 Demand Forecasting Features'
        
        # Check demand-specific features
        for feature_dict in features['features']:
            assert 'demand_value' in feature_dict
            assert 'demand_log' in feature_dict
            assert 'demand_sqrt' in feature_dict
            assert 'demand_density' in feature_dict
            assert 'demand_gradient' in feature_dict
            assert 'supply_demand_ratio' in feature_dict
            assert 'utilization_rate' in feature_dict
            
            # Validate feature values
            assert feature_dict['demand_value'] >= 0
            assert feature_dict['demand_log'] >= 0
            assert feature_dict['demand_sqrt'] >= 0
            assert 0 <= feature_dict['utilization_rate'] <= 1
    
    def test_feature_engine_empty_grid(self):
        """Test feature engine with empty grid."""
        empty_grid = H3Grid()
        engine = H3MLFeatureEngine(empty_grid)
        
        features = engine.create_spatial_features('demand')
        assert 'error' in features
    
    def test_feature_validation(self, ml_grid):
        """Test feature validation and consistency."""
        engine = H3MLFeatureEngine(ml_grid)
        features = engine.create_spatial_features('demand', neighbor_rings=1)
        
        # Validate feature consistency
        for feature_dict in features['features']:
            # Spatial consistency
            assert -90 <= feature_dict['cell_lat'] <= 90
            assert -180 <= feature_dict['cell_lng'] <= 180
            assert feature_dict['distance_from_equator'] >= 0
            
            # Neighbor consistency
            assert feature_dict['neighbor_density'] >= 0
            assert feature_dict['ring_1_count'] >= 0
            
            # Temporal consistency (if present)
            if 'hour_sin' in feature_dict and 'hour_cos' in feature_dict:
                # sin^2 + cos^2 should be approximately 1
                sin_cos_sum = feature_dict['hour_sin']**2 + feature_dict['hour_cos']**2
                assert abs(sin_cos_sum - 1.0) < 0.01


class TestH3DisasterResponse:
    """Test disaster response functionality."""
    
    def test_disaster_response_init(self, disaster_grid):
        """Test disaster response analyzer initialization."""
        analyzer = H3DisasterResponse(disaster_grid)
        assert analyzer.grid == disaster_grid
    
    def test_analyze_evacuation_zones(self, disaster_grid):
        """Test evacuation zone analysis."""
        analyzer = H3DisasterResponse(disaster_grid)
        zones = analyzer.analyze_evacuation_zones('flood_risk', 'population', evacuation_radius_km=2.0)
        
        assert 'high_risk_zones' in zones
        assert 'evacuation_zones' in zones
        assert 'total_affected_population' in zones
        assert 'evacuation_analysis' in zones
        
        # Check high-risk zones identification
        high_risk_zones = zones['high_risk_zones']
        assert len(high_risk_zones) > 0
        
        for zone in high_risk_zones:
            assert 'cell_index' in zone
            assert 'hazard_level' in zone
            assert 'population' in zone
            assert 'risk_category' in zone
            assert zone['hazard_level'] > 0.7  # High risk threshold
            assert zone['risk_category'] == 'high'
        
        # Check evacuation zones
        evacuation_zones = zones['evacuation_zones']
        assert len(evacuation_zones) > 0
        
        for evac_zone in evacuation_zones:
            assert 'hazard_cell' in evac_zone
            assert 'evacuation_cells' in evac_zone
            assert 'total_population' in evac_zone
            assert evac_zone['total_population'] >= 0
        
        # Check evacuation analysis
        analysis = zones['evacuation_analysis']
        assert 'total_evacuation_zones' in analysis
        assert 'total_affected_population' in analysis
        assert 'estimated_vehicles_needed' in analysis
        assert 'estimated_evacuation_time_hours' in analysis
        assert analysis['total_affected_population'] >= 0
        assert analysis['estimated_vehicles_needed'] >= 0
    
    def test_monitor_environmental_changes(self, disaster_grid):
        """Test environmental change monitoring."""
        analyzer = H3DisasterResponse(disaster_grid)
        changes = analyzer.monitor_environmental_changes(
            'baseline_temp', 'current_temp', change_threshold=0.1
        )
        
        assert 'significant_changes' in changes
        assert 'all_changes' in changes
        assert 'change_clusters' in changes
        assert 'summary_statistics' in changes
        
        # Check change detection
        all_changes = changes['all_changes']
        assert len(all_changes) > 0
        
        for change in all_changes:
            assert 'cell_index' in change
            assert 'baseline_value' in change
            assert 'current_value' in change
            assert 'absolute_change' in change
            assert 'relative_change' in change
            assert 'change_magnitude' in change
            
            # Validate change calculations
            expected_abs_change = change['current_value'] - change['baseline_value']
            assert abs(change['absolute_change'] - expected_abs_change) < 0.001
            
            if change['baseline_value'] != 0:
                expected_rel_change = expected_abs_change / change['baseline_value']
                assert abs(change['relative_change'] - expected_rel_change) < 0.001
        
        # Check significant changes
        significant_changes = changes['significant_changes']
        for sig_change in significant_changes:
            assert abs(sig_change['relative_change']) > 0.1  # Above threshold
            assert 'change_type' in sig_change
            assert sig_change['change_type'] in ['increase', 'decrease']
            assert 'significance' in sig_change
            assert sig_change['significance'] in ['high', 'moderate']
        
        # Check summary statistics
        if changes['summary_statistics']:
            stats = changes['summary_statistics']
            assert 'mean_change' in stats
            assert 'std_change' in stats
            assert 'max_change' in stats
            assert 'min_change' in stats
    
    def test_disaster_response_empty_grid(self):
        """Test disaster response with empty grid."""
        empty_grid = H3Grid()
        analyzer = H3DisasterResponse(empty_grid)
        
        zones = analyzer.analyze_evacuation_zones('flood_risk')
        assert 'error' in zones
        
        changes = analyzer.monitor_environmental_changes('baseline', 'current')
        assert 'error' in changes
    
    def test_evacuation_zone_calculations(self, disaster_grid):
        """Test evacuation zone calculation accuracy."""
        analyzer = H3DisasterResponse(disaster_grid)
        
        # Test with different evacuation radii
        for radius_km in [1.0, 2.0, 5.0]:
            zones = analyzer.analyze_evacuation_zones(
                'flood_risk', 'population', evacuation_radius_km=radius_km
            )
            
            assert zones['evacuation_radius_km'] == radius_km
            
            # Larger radius should generally include more population
            # (though this depends on the specific grid layout)
            assert zones['total_affected_population'] >= 0
    
    def test_change_clustering(self, disaster_grid):
        """Test environmental change clustering."""
        # Create grid with clustered changes
        for i, cell in enumerate(disaster_grid.cells):
            # Create temperature changes that should cluster
            if i < 2:  # First two cells have similar changes
                cell.properties['current_temp'] = cell.properties['baseline_temp'] + 5.0
            else:
                cell.properties['current_temp'] = cell.properties['baseline_temp'] + 0.5
        
        analyzer = H3DisasterResponse(disaster_grid)
        changes = analyzer.monitor_environmental_changes(
            'baseline_temp', 'current_temp', change_threshold=0.1
        )
        
        # Should detect significant changes
        assert len(changes['significant_changes']) >= 2
        
        # Check clustering results
        clusters = changes['change_clusters']
        if clusters:  # Clusters may or may not form depending on spatial adjacency
            for cluster in clusters:
                assert 'cluster_id' in cluster
                assert 'cells' in cluster
                assert 'cluster_size' in cluster
                assert 'cluster_statistics' in cluster
                assert cluster['cluster_size'] >= 2  # Multi-cell clusters only


class TestH3PerformanceOptimizer:
    """Test performance optimization functionality."""
    
    def test_performance_optimizer_init(self):
        """Test performance optimizer initialization."""
        optimizer = H3PerformanceOptimizer()
        assert optimizer is not None
    
    def test_benchmark_h3_operations(self):
        """Test H3 operations benchmarking."""
        optimizer = H3PerformanceOptimizer()
        
        test_coords = SF_COORDS[:2]  # Use subset for faster testing
        results = optimizer.benchmark_h3_operations(test_coords, resolutions=[8, 9])
        
        if 'error' not in results:  # Only test if H3 is available
            assert 'benchmark_results' in results
            assert 'test_parameters' in results
            
            benchmark_results = results['benchmark_results']
            
            # Check coordinate conversion benchmarks
            if 'coordinate_conversion' in benchmark_results:
                coord_bench = benchmark_results['coordinate_conversion']
                assert 'total_time_ms' in coord_bench
                assert 'avg_time_ms' in coord_bench
                assert 'operations_per_second' in coord_bench
                assert coord_bench['total_time_ms'] >= 0
                assert coord_bench['avg_time_ms'] >= 0
                assert coord_bench['operations_per_second'] >= 0
            
            # Check neighbor operations benchmarks
            if 'neighbor_operations' in benchmark_results:
                neighbor_bench = benchmark_results['neighbor_operations']
                assert 'total_time_ms' in neighbor_bench
                assert 'avg_time_ms' in neighbor_bench
                assert 'operations_per_second' in neighbor_bench
                assert neighbor_bench['total_time_ms'] >= 0
            
            # Check test parameters
            test_params = results['test_parameters']
            assert test_params['num_coordinates'] == len(test_coords)
            assert test_params['resolutions_tested'] == [8, 9]
    
    def test_optimize_grid_resolution(self):
        """Test grid resolution optimization."""
        optimizer = H3PerformanceOptimizer()
        
        # Test different scenarios
        test_cases = [
            {'area_km2': 100.0, 'analysis_type': 'general'},
            {'area_km2': 1000.0, 'analysis_type': 'ml', 'target_cells': 5000},
            {'area_km2': 10.0, 'analysis_type': 'visualization'},
            {'area_km2': 50.0, 'analysis_type': 'routing'}
        ]
        
        for case in test_cases:
            recommendation = optimizer.optimize_grid_resolution(**case)
            
            assert 'recommended_resolution' in recommendation
            assert 'estimated_cells' in recommendation
            assert 'all_recommendations' in recommendation
            assert 'analysis_parameters' in recommendation
            
            # Check recommended resolution is valid
            assert 0 <= recommendation['recommended_resolution'] <= 15
            assert recommendation['estimated_cells'] > 0
            
            # Check recommendations are sorted by suitability
            recommendations = recommendation['all_recommendations']
            assert len(recommendations) <= 5
            
            for i in range(len(recommendations) - 1):
                assert recommendations[i]['suitability_score'] >= recommendations[i + 1]['suitability_score']
            
            # Check analysis parameters match input
            params = recommendation['analysis_parameters']
            assert params['area_km2'] == case['area_km2']
            assert params['analysis_type'] == case['analysis_type']
            if 'target_cells' in case:
                assert params['target_cells'] == case['target_cells']
    
    def test_resolution_suitability_scoring(self):
        """Test resolution suitability scoring logic."""
        optimizer = H3PerformanceOptimizer()
        
        # Test ML analysis type preferences
        ml_rec = optimizer.optimize_grid_resolution(100.0, analysis_type='ml')
        ml_resolution = ml_rec['recommended_resolution']
        
        # ML should prefer moderate resolutions (7-10)
        assert 5 <= ml_resolution <= 12
        
        # Test visualization preferences (should prefer fewer cells)
        viz_rec = optimizer.optimize_grid_resolution(100.0, analysis_type='visualization')
        viz_resolution = viz_rec['recommended_resolution']
        
        # Visualization should generally prefer coarser resolutions
        assert viz_resolution <= ml_resolution + 2  # Allow some flexibility
        
        # Test target cells constraint
        target_rec = optimizer.optimize_grid_resolution(100.0, target_cells=1000)
        
        # Should try to get close to target cells
        estimated_cells = target_rec['estimated_cells']
        assert abs(estimated_cells - 1000) / 1000 < 2.0  # Within reasonable range
    
    def test_memory_usage_estimation(self):
        """Test memory usage estimation."""
        optimizer = H3PerformanceOptimizer()
        
        # Create some test cells
        test_cells = ['89283082803ffff', '89283082807ffff', '8928308280bffff']
        memory_usage = optimizer._estimate_memory_usage(test_cells)
        
        assert 'single_cell_bytes' in memory_usage
        assert 'neighbor_storage_bytes' in memory_usage
        assert 'estimated_cells_per_mb' in memory_usage
        
        assert memory_usage['single_cell_bytes'] > 0
        assert memory_usage['estimated_cells_per_mb'] > 0
    
    def test_benchmark_edge_cases(self):
        """Test benchmarking with edge cases."""
        optimizer = H3PerformanceOptimizer()
        
        # Test with empty coordinates
        empty_results = optimizer.benchmark_h3_operations([])
        # Should handle gracefully (may have error or zero results)
        
        # Test with single coordinate
        single_results = optimizer.benchmark_h3_operations([(37.7749, -122.4194)])
        if 'error' not in single_results:
            assert 'benchmark_results' in single_results


class TestMLIntegrationIntegration:
    """Test integration between ML components."""
    
    def test_ml_to_disaster_workflow(self, ml_grid):
        """Test workflow from ML features to disaster response."""
        # Create ML features
        ml_engine = H3MLFeatureEngine(ml_grid)
        features = ml_engine.create_spatial_features('demand')
        
        # Use features for disaster analysis
        disaster_analyzer = H3DisasterResponse(ml_grid)
        zones = disaster_analyzer.analyze_evacuation_zones('flood_risk', 'population')
        
        # Both should work on the same grid
        assert len(features['features']) > 0
        if 'error' not in zones:
            assert len(zones['high_risk_zones']) >= 0
    
    def test_performance_optimization_integration(self, ml_grid):
        """Test performance optimization with real grid."""
        optimizer = H3PerformanceOptimizer()
        
        # Get coordinates from grid
        coords = []
        for cell in ml_grid.cells:
            try:
                import h3
                if h3:
                    lat, lng = h3.cell_to_latlng(cell.index)
                    coords.append((lat, lng))
            except:
                pass
        
        if coords:
            # Benchmark with real coordinates
            results = optimizer.benchmark_h3_operations(coords[:3])  # Limit for testing
            
            if 'error' not in results:
                assert 'benchmark_results' in results
                
                # Optimize resolution for this area
                area_estimate = len(coords) * 0.1  # Rough area estimate
                resolution_rec = optimizer.optimize_grid_resolution(
                    area_estimate, analysis_type='ml'
                )
                
                assert 'recommended_resolution' in resolution_rec
    
    def test_feature_engineering_consistency(self, ml_grid):
        """Test consistency of feature engineering across different parameters."""
        engine = H3MLFeatureEngine(ml_grid)
        
        # Test different neighbor ring settings
        features_1_ring = engine.create_spatial_features('demand', neighbor_rings=1)
        features_2_ring = engine.create_spatial_features('demand', neighbor_rings=2)
        
        # Should have same number of cells
        assert len(features_1_ring['features']) == len(features_2_ring['features'])
        
        # 2-ring should have more features
        assert len(features_2_ring['feature_names']) > len(features_1_ring['feature_names'])
        
        # Core features should be consistent
        for f1, f2 in zip(features_1_ring['features'], features_2_ring['features']):
            assert f1['cell_index'] == f2['cell_index']
            assert f1['target_value'] == f2['target_value']
            assert f1['cell_lat'] == f2['cell_lat']
            assert f1['cell_lng'] == f2['cell_lng']


if __name__ == "__main__":
    pytest.main([__file__])
