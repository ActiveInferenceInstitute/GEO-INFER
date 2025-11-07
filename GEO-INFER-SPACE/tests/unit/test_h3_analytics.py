"""
Tests for H3 analytics module.

Test suite covering spatial analysis, clustering, density analysis,
network analysis, and temporal analysis for H3 grids.
"""

import pytest
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

from geo_infer_space.h3.core import H3Grid, H3Cell
from geo_infer_space.h3.analytics import (
    H3SpatialAnalyzer, H3ClusterAnalyzer, H3DensityAnalyzer,
    H3NetworkAnalyzer, H3TemporalAnalyzer
)

# Test data
SF_LAT, SF_LNG = 37.7749, -122.4194
RESOLUTION = 9


@pytest.fixture
def sample_grid():
    """Create a sample H3 grid for testing."""
    grid = H3Grid(resolution=RESOLUTION)
    
    # Add cells with various properties
    cells_data = [
        {"lat": 37.7749, "lng": -122.4194, "population": 1000, "crime_count": 5},
        {"lat": 37.7759, "lng": -122.4184, "population": 1200, "crime_count": 3},
        {"lat": 37.7739, "lng": -122.4204, "population": 800, "crime_count": 8},
        {"lat": 37.7769, "lng": -122.4174, "population": 1500, "crime_count": 2},
        {"lat": 37.7729, "lng": -122.4214, "population": 600, "crime_count": 12},
    ]
    
    for data in cells_data:
        cell = H3Cell.from_coordinates(data["lat"], data["lng"], RESOLUTION)
        cell.properties.update({
            "population": data["population"],
            "crime_count": data["crime_count"],
            "density": data["population"] / 100,  # Simplified density
            "timestamp": datetime.now().isoformat(),
            "activity_level": data["population"] * 0.01
        })
        grid.add_cell(cell)
    
    return grid


@pytest.fixture
def temporal_grid():
    """Create a grid with temporal data for testing."""
    grid = H3Grid(resolution=RESOLUTION)
    
    # Create cells with temporal patterns
    base_time = datetime(2023, 1, 1, 8, 0, 0)  # 8 AM
    
    for i in range(24):  # 24 hours of data
        for j in range(3):  # 3 cells per hour
            cell = H3Cell.from_coordinates(
                SF_LAT + (i * 0.001), 
                SF_LNG + (j * 0.001), 
                RESOLUTION
            )
            
            # Create temporal patterns (higher activity during business hours)
            hour = i
            if 8 <= hour <= 18:  # Business hours
                activity = 100 + (j * 20)
            elif 19 <= hour <= 22:  # Evening
                activity = 80 + (j * 15)
            else:  # Night/early morning
                activity = 20 + (j * 5)
            
            cell.properties.update({
                "timestamp": (base_time + timedelta(hours=i)).isoformat(),
                "trip_count": activity,
                "hour": hour
            })
            grid.add_cell(cell)
    
    return grid


class TestH3SpatialAnalyzer:
    """Test spatial analysis functionality."""
    
    def test_spatial_analyzer_init(self, sample_grid):
        """Test spatial analyzer initialization."""
        analyzer = H3SpatialAnalyzer(sample_grid)
        assert analyzer.grid == sample_grid
    
    def test_analyze_spatial_autocorrelation(self, sample_grid):
        """Test spatial autocorrelation analysis."""
        analyzer = H3SpatialAnalyzer(sample_grid)
        result = analyzer.analyze_spatial_autocorrelation("population")
        
        assert "morans_i" in result
        assert "interpretation" in result
        assert "n_observations" in result
        assert "method" in result
        
        assert isinstance(result["morans_i"], float)
        assert isinstance(result["interpretation"], str)
        assert result["n_observations"] > 0
    
    def test_detect_hotspots_getis_ord(self, sample_grid):
        """Test hotspot detection using Getis-Ord method."""
        analyzer = H3SpatialAnalyzer(sample_grid)
        result = analyzer.detect_hotspots("crime_count", method="getis_ord")
        
        assert "method" in result
        assert "hotspots" in result
        assert "coldspots" in result
        assert "total_cells_analyzed" in result
        
        assert result["method"] == "Getis-Ord Gi*"
        assert isinstance(result["hotspots"], list)
        assert isinstance(result["coldspots"], list)
        assert result["total_cells_analyzed"] > 0
    
    def test_detect_hotspots_local_morans(self, sample_grid):
        """Test hotspot detection using Local Moran's I method."""
        analyzer = H3SpatialAnalyzer(sample_grid)
        result = analyzer.detect_hotspots("population", method="local_morans")
        
        assert "method" in result
        assert "hotspots" in result
        assert "coldspots" in result
        assert "outliers" in result
        
        assert result["method"] == "Local Morans I"
        assert isinstance(result["hotspots"], list)
        assert isinstance(result["coldspots"], list)
        assert isinstance(result["outliers"], list)
    
    def test_empty_grid_handling(self):
        """Test handling of empty grid."""
        empty_grid = H3Grid(resolution=RESOLUTION)
        analyzer = H3SpatialAnalyzer(empty_grid)
        
        result = analyzer.analyze_spatial_autocorrelation("population")
        assert "error" in result
        
        result = analyzer.detect_hotspots("population")
        assert "error" in result


class TestH3ClusterAnalyzer:
    """Test clustering analysis functionality."""
    
    def test_cluster_analyzer_init(self, sample_grid):
        """Test cluster analyzer initialization."""
        analyzer = H3ClusterAnalyzer(sample_grid)
        assert analyzer.grid == sample_grid
    
    def test_density_based_clustering(self, sample_grid):
        """Test density-based clustering."""
        analyzer = H3ClusterAnalyzer(sample_grid)
        result = analyzer.density_based_clustering("population", eps_rings=1)
        
        assert "clusters" in result
        assert "n_clusters" in result
        assert "n_noise" in result
        assert "method" in result
        
        assert isinstance(result["clusters"], list)
        assert isinstance(result["n_clusters"], int)
        assert isinstance(result["n_noise"], int)
        assert result["method"] == "H3-adapted DBSCAN"
    
    def test_hierarchical_clustering(self, sample_grid):
        """Test hierarchical clustering."""
        analyzer = H3ClusterAnalyzer(sample_grid)
        result = analyzer.hierarchical_clustering("density")
        
        assert "clusters" in result
        assert "method" in result
        assert "distance_matrix_size" in result
        
        assert isinstance(result["clusters"], list)
        assert "Hierarchical clustering" in result["method"]
    
    def test_clustering_with_insufficient_data(self):
        """Test clustering with insufficient data."""
        small_grid = H3Grid(resolution=RESOLUTION)
        cell = H3Cell.from_coordinates(SF_LAT, SF_LNG, RESOLUTION)
        cell.properties["population"] = 100
        small_grid.add_cell(cell)
        
        analyzer = H3ClusterAnalyzer(small_grid)
        result = analyzer.density_based_clustering("population")
        
        assert "error" in result


class TestH3DensityAnalyzer:
    """Test density analysis functionality."""
    
    def test_density_analyzer_init(self, sample_grid):
        """Test density analyzer initialization."""
        analyzer = H3DensityAnalyzer(sample_grid)
        assert analyzer.grid == sample_grid
    
    def test_calculate_kernel_density(self, sample_grid):
        """Test kernel density estimation."""
        analyzer = H3DensityAnalyzer(sample_grid)
        result = analyzer.calculate_kernel_density("population", bandwidth_rings=2)
        
        assert "density_surface" in result
        assert "statistics" in result
        assert "bandwidth_rings" in result
        assert "kernel_type" in result
        assert "method" in result
        
        assert isinstance(result["density_surface"], list)
        assert len(result["density_surface"]) > 0
        assert result["bandwidth_rings"] == 2
        
        # Check statistics
        stats = result["statistics"]
        assert "mean_density" in stats
        assert "max_density" in stats
        assert "min_density" in stats
    
    def test_kernel_density_different_kernels(self, sample_grid):
        """Test different kernel types."""
        analyzer = H3DensityAnalyzer(sample_grid)
        
        for kernel_type in ["gaussian", "uniform", "triangular"]:
            result = analyzer.calculate_kernel_density(
                "population", 
                bandwidth_rings=1, 
                kernel_type=kernel_type
            )
            assert result["kernel_type"] == kernel_type
            assert len(result["density_surface"]) > 0
    
    def test_analyze_density_patterns(self, sample_grid):
        """Test density pattern analysis."""
        analyzer = H3DensityAnalyzer(sample_grid)
        result = analyzer.analyze_density_patterns("population")
        
        assert "high_density_clusters" in result
        assert "low_density_gaps" in result
        assert "density_gradients" in result
        assert "thresholds" in result
        assert "pattern_summary" in result
        
        # Check thresholds
        thresholds = result["thresholds"]
        assert "q25" in thresholds
        assert "q75" in thresholds
        assert "mean" in thresholds
        assert "std" in thresholds
        
        # Check pattern summary
        summary = result["pattern_summary"]
        assert "n_high_density" in summary
        assert "n_low_density" in summary
        assert "n_significant_gradients" in summary


class TestH3NetworkAnalyzer:
    """Test network analysis functionality."""
    
    def test_network_analyzer_init(self, sample_grid):
        """Test network analyzer initialization."""
        analyzer = H3NetworkAnalyzer(sample_grid)
        assert analyzer.grid == sample_grid
    
    def test_analyze_flow_patterns(self, sample_grid):
        """Test flow pattern analysis."""
        # Add flow data to cells
        cells = list(sample_grid.cells)
        if len(cells) >= 2:
            cells[0].properties["pickup_h3"] = cells[0].index
            cells[0].properties["dropoff_h3"] = cells[1].index
            cells[0].properties["trip_count"] = 10
            
            cells[1].properties["pickup_h3"] = cells[1].index
            cells[1].properties["dropoff_h3"] = cells[0].index
            cells[1].properties["trip_count"] = 5
        
        analyzer = H3NetworkAnalyzer(sample_grid)
        result = analyzer.analyze_flow_patterns("pickup_h3", "dropoff_h3", "trip_count")
        
        assert "flows" in result
        assert "total_flows" in result
        assert "flow_analysis" in result
        assert "network_metrics" in result
        
        if result["total_flows"] > 0:
            assert len(result["flows"]) > 0
            
            flow_analysis = result["flow_analysis"]
            assert "top_flows" in flow_analysis
            assert "unique_od_pairs" in flow_analysis
    
    def test_calculate_accessibility(self, sample_grid):
        """Test accessibility calculation."""
        analyzer = H3NetworkAnalyzer(sample_grid)
        result = analyzer.calculate_accessibility(max_rings=2)
        
        assert "accessibility_scores" in result
        assert "most_accessible" in result
        assert "least_accessible" in result
        assert "max_rings_analyzed" in result
        
        scores = result["accessibility_scores"]
        assert len(scores) > 0
        
        for score in scores:
            assert "cell_index" in score
            assert "accessibility_score" in score
            assert "reachable_cells" in score
    
    def test_detect_network_communities(self, sample_grid):
        """Test network community detection."""
        # Add flow properties to cells
        for cell in sample_grid.cells:
            cell.properties["flow_volume"] = 0.2  # Above threshold
        
        analyzer = H3NetworkAnalyzer(sample_grid)
        result = analyzer.detect_network_communities(flow_threshold=0.1)
        
        assert "communities" in result
        assert "n_communities" in result
        assert "flow_threshold" in result
        assert "method" in result
        
        assert isinstance(result["communities"], list)
        assert result["flow_threshold"] == 0.1


class TestH3TemporalAnalyzer:
    """Test temporal analysis functionality."""
    
    def test_temporal_analyzer_init(self, temporal_grid):
        """Test temporal analyzer initialization."""
        analyzer = H3TemporalAnalyzer(temporal_grid)
        assert analyzer.grid == temporal_grid
    
    def test_analyze_temporal_patterns(self, temporal_grid):
        """Test temporal pattern analysis."""
        analyzer = H3TemporalAnalyzer(temporal_grid)
        result = analyzer.analyze_temporal_patterns("timestamp", "trip_count", "hour")
        
        assert "temporal_patterns" in result
        assert "aggregated_data" in result
        assert "statistics" in result
        assert "temporal_resolution" in result
        assert "method" in result
        
        patterns = result["temporal_patterns"]
        assert "peak_periods" in patterns
        assert "temporal_variability" in patterns
        assert "pattern_type" in patterns
        
        # Check peak periods
        peak_periods = patterns["peak_periods"]
        assert isinstance(peak_periods, list)
        if peak_periods:
            peak = peak_periods[0]
            assert "period" in peak
            assert "period_name" in peak
            assert "mean_value" in peak
    
    def test_detect_temporal_anomalies_zscore(self, temporal_grid):
        """Test temporal anomaly detection using Z-score."""
        analyzer = H3TemporalAnalyzer(temporal_grid)
        result = analyzer.detect_temporal_anomalies("timestamp", "trip_count", method="zscore", threshold=1.5)
        
        assert "anomalies" in result
        assert "method" in result
        assert "threshold" in result
        assert "total_data_points" in result
        assert "anomaly_rate" in result
        
        assert result["method"] == "zscore"
        assert result["threshold"] == 1.5
        assert isinstance(result["anomalies"], list)
    
    def test_detect_temporal_anomalies_iqr(self, temporal_grid):
        """Test temporal anomaly detection using IQR."""
        analyzer = H3TemporalAnalyzer(temporal_grid)
        result = analyzer.detect_temporal_anomalies("timestamp", "trip_count", method="iqr", threshold=1.5)
        
        assert "anomalies" in result
        assert "method" in result
        assert result["method"] == "iqr"
        
        anomalies = result["anomalies"]
        for anomaly in anomalies:
            assert "cell_index" in anomaly
            assert "timestamp" in anomaly
            assert "value" in anomaly
            assert "anomaly_type" in anomaly
            assert anomaly["anomaly_type"] in ["high", "low"]
    
    def test_temporal_patterns_different_resolutions(self, temporal_grid):
        """Test temporal patterns with different resolutions."""
        analyzer = H3TemporalAnalyzer(temporal_grid)
        
        for resolution in ["hour", "day", "week", "month"]:
            result = analyzer.analyze_temporal_patterns("timestamp", "trip_count", resolution)
            assert result["temporal_resolution"] == resolution
            assert "temporal_patterns" in result
    
    def test_insufficient_temporal_data(self):
        """Test handling of insufficient temporal data."""
        small_grid = H3Grid(resolution=RESOLUTION)
        cell = H3Cell.from_coordinates(SF_LAT, SF_LNG, RESOLUTION)
        cell.properties.update({
            "timestamp": datetime.now().isoformat(),
            "value": 100
        })
        small_grid.add_cell(cell)
        
        analyzer = H3TemporalAnalyzer(small_grid)
        result = analyzer.detect_temporal_anomalies("timestamp", "value")
        
        assert "error" in result


class TestAnalyticsIntegration:
    """Test integration between different analytics modules."""
    
    def test_multi_analyzer_workflow(self, sample_grid):
        """Test using multiple analyzers together."""
        # Spatial analysis
        spatial_analyzer = H3SpatialAnalyzer(sample_grid)
        spatial_result = spatial_analyzer.analyze_spatial_autocorrelation("population")
        
        # Density analysis
        density_analyzer = H3DensityAnalyzer(sample_grid)
        density_result = density_analyzer.calculate_kernel_density("population")
        
        # Clustering analysis
        cluster_analyzer = H3ClusterAnalyzer(sample_grid)
        cluster_result = cluster_analyzer.density_based_clustering("population")
        
        # All analyses should complete successfully
        assert "morans_i" in spatial_result
        assert "density_surface" in density_result
        assert "clusters" in cluster_result
        
        # Results should be consistent
        assert len(density_result["density_surface"]) == len(sample_grid.cells)
    
    def test_analytics_with_missing_data(self, sample_grid):
        """Test analytics handling of missing data."""
        # Remove some properties from cells
        cells = list(sample_grid.cells)
        if cells:
            cells[0].properties.pop("population", None)
        
        spatial_analyzer = H3SpatialAnalyzer(sample_grid)
        result = spatial_analyzer.analyze_spatial_autocorrelation("population")
        
        # Should handle missing data gracefully
        assert "n_observations" in result
        assert result["n_observations"] == len(sample_grid.cells) - 1


if __name__ == "__main__":
    pytest.main([__file__])
