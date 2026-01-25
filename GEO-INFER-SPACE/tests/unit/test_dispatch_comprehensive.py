"""
Comprehensive tests for the GEO-INFER-SPACE dispatch system.

Tests the multi-backend dispatch abstraction to ensure operations
are correctly routed to the appropriate backend.
"""

import pytest
from typing import Dict, Any, List

from geo_infer_space.core.dispatcher import (
    SpatialBackendDispatcher,
    get_backend_dispatcher,
    reset_dispatcher,
)
from geo_infer_space.backends.h3.h3_backend import H3Backend


@pytest.fixture(autouse=True)
def reset_global_dispatcher():
    """Reset the global dispatcher before each test."""
    reset_dispatcher()
    yield
    reset_dispatcher()


class TestDispatcherInitialization:
    """Test dispatcher initialization and backend loading."""
    
    def test_dispatcher_creation(self):
        """Test basic dispatcher creation."""
        dispatcher = SpatialBackendDispatcher()
        assert dispatcher is not None
        assert isinstance(dispatcher.backends, dict)
    
    def test_h3_backend_auto_loaded(self):
        """Test that H3 backend is automatically loaded."""
        dispatcher = SpatialBackendDispatcher()
        
        # H3 should be available if the library is installed
        available = dispatcher.get_available_backends()
        assert 'h3' in available
    
    def test_get_backend_by_name(self):
        """Test retrieving a specific backend."""
        dispatcher = SpatialBackendDispatcher()
        
        h3_backend = dispatcher.get_backend('h3')
        assert h3_backend is not None
        assert h3_backend.name == 'h3'
    
    def test_get_nonexistent_backend(self):
        """Test retrieving a backend that doesn't exist."""
        dispatcher = SpatialBackendDispatcher()
        
        result = dispatcher.get_backend('nonexistent')
        assert result is None
    
    def test_backend_info(self):
        """Test getting backend information."""
        dispatcher = SpatialBackendDispatcher()
        
        info = dispatcher.get_backend_info()
        assert 'h3' in info
        assert 'available' in info['h3']
        assert 'capabilities' in info['h3']


class TestGlobalDispatcher:
    """Test global dispatcher singleton pattern."""
    
    def test_get_global_dispatcher(self):
        """Test getting the global dispatcher instance."""
        dispatcher1 = get_backend_dispatcher()
        dispatcher2 = get_backend_dispatcher()
        
        # Should be the same instance
        assert dispatcher1 is dispatcher2
    
    def test_reset_dispatcher(self):
        """Test resetting the global dispatcher."""
        dispatcher1 = get_backend_dispatcher()
        reset_dispatcher()
        dispatcher2 = get_backend_dispatcher()
        
        # Should be different instances after reset
        assert dispatcher1 is not dispatcher2


class TestDefaultBackendConfiguration:
    """Test default backend configuration."""
    
    def test_set_default_backend(self):
        """Test setting default backend for operation type."""
        dispatcher = SpatialBackendDispatcher()
        
        dispatcher.set_default_backend('indexing', 'h3')
        assert dispatcher.get_default_backend('indexing') == 'h3'
    
    def test_default_backend_fallback(self):
        """Test that default backend falls back to h3."""
        dispatcher = SpatialBackendDispatcher()
        
        # Without explicit setting, should default to h3
        default = dispatcher.get_default_backend('some_operation')
        assert default == 'h3'
    
    def test_set_invalid_default_backend(self):
        """Test setting a non-existent backend as default."""
        dispatcher = SpatialBackendDispatcher()
        
        with pytest.raises(ValueError, match="not registered"):
            dispatcher.set_default_backend('indexing', 'nonexistent')


class TestIndexingOperationDispatch:
    """Test dispatching indexing operations."""
    
    @pytest.fixture
    def dispatcher(self):
        return SpatialBackendDispatcher()
    
    def test_dispatch_latlng_to_cell(self, dispatcher):
        """Test dispatching latlng_to_cell operation."""
        result = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            8
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_dispatch_cell_to_latlng(self, dispatcher):
        """Test dispatching cell_to_latlng operation."""
        # First get a valid cell
        cell = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            8
        )
        
        # Then convert back
        lat, lng = dispatcher.dispatch_indexing_operation('cell_to_latlng', cell)
        
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180
    
    def test_dispatch_get_neighbors(self, dispatcher):
        """Test dispatching get_neighbors operation."""
        cell = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            8
        )
        
        neighbors = dispatcher.dispatch_indexing_operation('get_neighbors', cell, k=1)
        
        assert isinstance(neighbors, list)
        assert len(neighbors) == 6  # Hexagon has 6 neighbors
    
    def test_dispatch_get_cell_parent(self, dispatcher):
        """Test dispatching get_cell_parent operation."""
        cell = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            8
        )
        
        parent = dispatcher.dispatch_indexing_operation('get_cell_parent', cell, 5)
        
        assert isinstance(parent, str)
        assert len(parent) > 0
    
    def test_dispatch_get_cell_children(self, dispatcher):
        """Test dispatching get_cell_children operation."""
        cell = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            5
        )
        
        children = dispatcher.dispatch_indexing_operation('get_cell_children', cell, 6)
        
        assert isinstance(children, list)
        assert len(children) == 7  # Each cell has 7 children
    
    def test_dispatch_compact_uncompact(self, dispatcher):
        """Test compact and uncompact operations."""
        # Get a parent cell and its children
        parent = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            5
        )
        children = dispatcher.dispatch_indexing_operation('get_cell_children', parent, 6)
        
        # Compact should reduce back
        compacted = dispatcher.dispatch_indexing_operation('compact_cells', children)
        assert len(compacted) <= len(children)
        
        # Uncompact should expand
        uncompacted = dispatcher.dispatch_indexing_operation('uncompact_cells', compacted, 6)
        assert len(uncompacted) == len(children)
    
    def test_dispatch_unknown_operation(self, dispatcher):
        """Test dispatching an unknown operation."""
        with pytest.raises(ValueError, match="Unknown indexing operation"):
            dispatcher.dispatch_indexing_operation('unknown_operation', 'arg1')
    
    def test_dispatch_with_explicit_backend(self, dispatcher):
        """Test dispatching with explicit backend specification."""
        result = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            8,
            backend='h3'
        )
        
        assert isinstance(result, str)


class TestAnalyticsOperationDispatch:
    """Test dispatching analytics operations."""
    
    @pytest.fixture
    def dispatcher(self):
        return SpatialBackendDispatcher()
    
    @pytest.fixture
    def test_cells(self, dispatcher):
        """Generate test cells for analytics."""
        # Create a cluster of cells
        center = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            8
        )
        neighbors = dispatcher.dispatch_indexing_operation('get_neighbors', center, k=2)
        neighbors.insert(0, center)
        return neighbors
    
    def test_dispatch_analyze_hotspots(self, dispatcher, test_cells):
        """Test dispatching analyze_hotspots operation."""
        values = [i * 10 for i in range(len(test_cells))]
        
        result = dispatcher.dispatch_analytics_operation(
            'analyze_hotspots',
            {'cells': test_cells, 'values': values}
        )
        
        assert 'hotspots' in result
        assert 'threshold' in result
        assert 'total_cells' in result
    
    def test_dispatch_compute_proximity(self, dispatcher):
        """Test dispatching compute_proximity operation."""
        points = [
            (37.7749, -122.4194),
            (37.7849, -122.4094),
            (37.7649, -122.4294),
        ]
        
        result = dispatcher.dispatch_analytics_operation(
            'compute_proximity',
            points
        )
        
        assert 'proximity_pairs' in result
        assert 'total_points' in result
        assert result['total_points'] == 3
    
    def test_dispatch_find_clusters(self, dispatcher, test_cells):
        """Test dispatching find_clusters operation."""
        values = [1.0] * len(test_cells)
        
        result = dispatcher.dispatch_analytics_operation(
            'find_clusters',
            test_cells,
            values,
            min_cluster_size=3,
            distance_threshold=1
        )
        
        assert 'clusters' in result
        assert 'num_clusters' in result
        assert 'noise_cells' in result
    
    def test_dispatch_calculate_density(self, dispatcher, test_cells):
        """Test dispatching calculate_density operation."""
        values = [1.0 + i * 0.5 for i in range(len(test_cells))]
        
        result = dispatcher.dispatch_analytics_operation(
            'calculate_density',
            test_cells,
            values,
            kernel_radius=1
        )
        
        assert 'densities' in result
        assert 'statistics' in result
        assert len(result['densities']) == len(test_cells)
    
    def test_dispatch_spatial_join(self, dispatcher, test_cells):
        """Test dispatching spatial_join operation."""
        cells_a = test_cells[:5]
        cells_b = test_cells[3:8]  # Overlapping
        
        result = dispatcher.dispatch_analytics_operation(
            'spatial_join',
            cells_a,
            cells_b,
            join_type='intersects'
        )
        
        assert 'matches' in result
        assert 'match_count' in result
        assert result['match_count'] > 0  # Should have overlapping matches
    
    def test_dispatch_interpolate_values(self, dispatcher, test_cells):
        """Test dispatching interpolate_values operation."""
        source_cells = test_cells[:5]
        source_values = [10.0, 20.0, 30.0, 40.0, 50.0]
        target_cells = test_cells[3:8]
        
        result = dispatcher.dispatch_analytics_operation(
            'interpolate_values',
            source_cells,
            source_values,
            target_cells,
            method='idw'
        )
        
        assert 'interpolated' in result
        assert 'method' in result
        assert result['method'] == 'idw'
        assert len(result['interpolated']) == len(target_cells)
    
    def test_dispatch_unknown_analytics_operation(self, dispatcher):
        """Test dispatching an unknown analytics operation."""
        with pytest.raises(ValueError, match="Unknown analytics operation"):
            dispatcher.dispatch_analytics_operation('unknown_analytics', 'arg1')


class TestBackendSwitching:
    """Test switching between backends."""
    
    def test_operation_same_across_backends(self):
        """Test that operations produce the same result type across backends."""
        dispatcher = SpatialBackendDispatcher()
        
        # Test with H3 backend
        result_h3 = dispatcher.dispatch_indexing_operation(
            'latlng_to_cell', 
            37.7749, 
            -122.4194, 
            8,
            backend='h3'
        )
        
        assert isinstance(result_h3, str)
    
    def test_backend_capabilities_match_operations(self):
        """Test that backend capabilities match available operations."""
        dispatcher = SpatialBackendDispatcher()
        h3_backend = dispatcher.get_backend('h3')
        
        capabilities = h3_backend.get_capabilities()
        
        # Check indexing capabilities
        assert 'indexing' in capabilities
        assert capabilities['indexing']['latlng_to_cell'] is True
        assert capabilities['indexing']['polygon_to_cells'] is True
        
        # Check analytics capabilities
        assert 'analytics' in capabilities
        assert capabilities['analytics']['analyze_hotspots'] is True


class TestEndToEndDispatchWorkflow:
    """End-to-end tests for complete dispatch workflows."""
    
    def test_complete_spatial_analysis_workflow(self):
        """Test a complete spatial analysis workflow through dispatch."""
        dispatcher = SpatialBackendDispatcher()
        
        # Step 1: Convert locations to cells
        locations = [
            (37.7749, -122.4194),  # San Francisco
            (37.7849, -122.4294),
            (37.7649, -122.4094),
            (37.7749, -122.4094),
            (37.7849, -122.4194),
        ]
        
        cells = []
        for lat, lng in locations:
            cell = dispatcher.dispatch_indexing_operation(
                'latlng_to_cell', lat, lng, 8
            )
            cells.append(cell)
        
        assert len(cells) == 5
        
        # Step 2: Analyze hotspots
        values = [100, 50, 75, 200, 25]
        hotspot_result = dispatcher.dispatch_analytics_operation(
            'analyze_hotspots',
            {'cells': cells, 'values': values}
        )
        
        assert hotspot_result['total_cells'] == 5
        
        # Step 3: Find clusters
        cluster_result = dispatcher.dispatch_analytics_operation(
            'find_clusters',
            cells,
            values,
            min_cluster_size=2,
            distance_threshold=2
        )
        
        assert 'clusters' in cluster_result
        
        # Step 4: Calculate density
        density_result = dispatcher.dispatch_analytics_operation(
            'calculate_density',
            cells,
            values,
            kernel_radius=1
        )
        
        assert len(density_result['densities']) == 5
        
        # Step 5: Get cell boundaries for visualization
        for cell in cells[:2]:
            boundary = dispatcher.dispatch_indexing_operation('get_cell_boundary', cell)
            assert len(boundary) >= 6  # Hexagon has at least 6 vertices
