"""Integration tests for GEO-INFER-SPACE integration."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from geo_infer_metagov.integrations.spatial import SpatialGovernanceIntegration


class TestSpatialIntegration:
    """Test suite for spatial governance integration."""
    
    @pytest.fixture
    def spatial_integration(self):
        """Create spatial integration instance."""
        return SpatialGovernanceIntegration()
    
    def test_integration_initialization(self, spatial_integration):
        """Test integration initializes correctly."""
        assert spatial_integration is not None
        # Should work even if SPACE module not available (graceful degradation)
    
    def test_index_governance_boundary(self, spatial_integration):
        """Test boundary indexing."""
        boundary = {
            'name': 'Test Region',
            'coordinates': [37.7749, -122.4194],  # San Francisco
            'area_km2': 1000
        }
        
        result = spatial_integration.index_governance_boundary(boundary, resolution=9)
        
        # Should return result even if SPACE not available
        assert 'indexed' in result
        # If SPACE available, should have cells
        if result.get('indexed'):
            assert 'cells' in result
            assert 'cell_count' in result
    
    def test_detect_jurisdictional_overlaps(self, spatial_integration):
        """Test overlap detection."""
        boundaries = [
            {
                'id': 'boundary1',
                'name': 'Region 1',
                'coordinates': [37.7749, -122.4194],
                'area_km2': 1000
            },
            {
                'id': 'boundary2',
                'name': 'Region 2',
                'coordinates': [37.7849, -122.4294],  # Close to boundary1
                'area_km2': 1200
            }
        ]
        
        result = spatial_integration.detect_jurisdictional_overlaps(boundaries, resolution=9)
        
        assert 'overlaps_detected' in result
        # May or may not detect overlaps depending on SPACE availability and actual coordinates
        if result.get('overlaps_detected'):
            assert 'overlaps' in result
            assert 'overlap_count' in result
    
    def test_map_entities_to_spatial_cells(self, spatial_integration):
        """Test entity to spatial cell mapping."""
        entities = [
            {
                'id': 'entity1',
                'jurisdiction': {
                    'name': 'Jurisdiction 1',
                    'coordinates': [37.7749, -122.4194]
                }
            },
            {
                'id': 'entity2',
                'jurisdiction': {
                    'name': 'Jurisdiction 2',
                    'coordinates': [37.7849, -122.4294]
                }
            }
        ]
        
        result = spatial_integration.map_governance_entities_to_spatial_cells(entities, resolution=9)
        
        assert 'mapped' in result
        if result.get('mapped'):
            assert 'entity_cell_mapping' in result
            assert 'total_entities' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



