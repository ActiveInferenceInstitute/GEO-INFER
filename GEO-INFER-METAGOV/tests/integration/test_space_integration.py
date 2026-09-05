"""Integration tests for GEO-INFER-SPACE integration.

These tests pin real behavior: bounds-to-polygon conversion (pure Python) and
real H3 cell counts / overlap outcomes through GEO-INFER-SPACE. Skips are
forbidden by the test contract, so SPACE availability is asserted outright.
"""

import pytest

from geo_infer_metagov.integrations.spatial import (
    SPACE_AVAILABLE,
    SpatialGovernanceIntegration,
    bounds_to_polygon,
)


class TestBoundsToPolygon:
    """Test bounds-to-polygon conversion (pure Python, no SPACE needed)."""

    def test_bounds_to_polygon_canonical_keys(self) -> None:
        polygon = bounds_to_polygon({'min_lat': 37.0, 'max_lat': 38.0,
                                     'min_lng': -123.0, 'max_lng': -122.0})
        assert polygon['type'] == 'Polygon'
        ring = polygon['coordinates'][0]
        assert ring[0] == [-123.0, 37.0]
        # Closed ring: first point equals last point
        assert ring[0] == ring[-1]
        # GeoJSON [lng, lat] ordering
        assert all(len(pt) == 2 and -123.0 <= pt[0] <= -122.0 for pt in ring)

    def test_bounds_to_polygon_compass_aliases(self) -> None:
        polygon = bounds_to_polygon({'south': 37.0, 'north': 38.0,
                                     'west': -123.0, 'east': -122.0})
        assert polygon == bounds_to_polygon({'min_lat': 37.0, 'max_lat': 38.0,
                                             'min_lng': -123.0, 'max_lng': -122.0})

    def test_bounds_to_polygon_missing_keys_raise(self) -> None:
        with pytest.raises(ValueError, match='extrema'):
            bounds_to_polygon({'min_lat': 37.0})

    def test_bounds_to_polygon_inverted_bounds_raise(self) -> None:
        with pytest.raises(ValueError, match='min exceeds max'):
            bounds_to_polygon({'min_lat': 38.0, 'max_lat': 37.0,
                               'min_lng': -123.0, 'max_lng': -122.0})


class TestSpatialIntegrationWithSpace:
    """Behavioral tests against the real GEO-INFER-SPACE backend."""

    @pytest.fixture
    def integration(self) -> SpatialGovernanceIntegration:
        assert SPACE_AVAILABLE, (
            "GEO-INFER-SPACE must be installed; these tests pin real behavior "
            "and cannot run against the degradation path"
        )
        return SpatialGovernanceIntegration()

    def test_index_point_boundary(self, integration: SpatialGovernanceIntegration) -> None:
        result = integration.index_governance_boundary(
            {'name': 'SF', 'coordinates': [37.7749, -122.4194]}, resolution=9
        )
        assert result['indexed'] is True
        assert result['cell_count'] == 1
        assert len(result['cells']) == 1
        assert result['cells'][0].startswith('8')  # H3 res-9 cells start with '8'

    def test_index_bounds_boundary(self, integration: SpatialGovernanceIntegration) -> None:
        result = integration.index_governance_boundary(
            {'name': 'Bay Area', 'bounds': {'min_lat': 37.0, 'max_lat': 38.0,
                                            'min_lng': -123.0, 'max_lng': -122.0}},
            resolution=7
        )
        assert result['indexed'] is True
        # A 1-degree box at res 7 must cover many cells, not silently zero
        assert result['cell_count'] > 10
        assert result['cell_count'] == len(set(result['cells']))

    def test_overlapping_boundaries_detected(self, integration: SpatialGovernanceIntegration) -> None:
        boundaries = [
            {'id': 'a', 'bounds': {'min_lat': 37.0, 'max_lat': 38.0,
                                   'min_lng': -123.0, 'max_lng': -122.0}},
            {'id': 'b', 'bounds': {'min_lat': 37.5, 'max_lat': 38.5,
                                   'min_lng': -122.5, 'max_lng': -121.5}},
        ]
        result = integration.detect_jurisdictional_overlaps(boundaries, resolution=7)
        assert result['overlaps_detected'] is True
        assert result['overlap_count'] >= 1
        overlap = result['overlaps'][0]
        assert {overlap['boundary_1'], overlap['boundary_2']} == {'a', 'b'}
        assert overlap['overlap_cell_count'] > 0
        assert overlap['severity'] in ('low', 'medium', 'high')

    def test_disjoint_boundaries_no_overlap(self, integration: SpatialGovernanceIntegration) -> None:
        boundaries = [
            {'id': 'a', 'bounds': {'min_lat': 10.0, 'max_lat': 11.0,
                                   'min_lng': 10.0, 'max_lng': 11.0}},
            {'id': 'b', 'bounds': {'min_lat': 40.0, 'max_lat': 41.0,
                                   'min_lng': 40.0, 'max_lng': 41.0}},
        ]
        result = integration.detect_jurisdictional_overlaps(boundaries, resolution=5)
        assert result['overlaps_detected'] is False
        assert result['overlap_count'] == 0

    def test_coverage_analysis(self, integration: SpatialGovernanceIntegration) -> None:
        region = {'bounds': {'min_lat': 37.0, 'max_lat': 38.0,
                             'min_lng': -123.0, 'max_lng': -122.0}}
        structure = {
            'entities': [
                {'entity_id': 'e1', 'jurisdiction': {
                    'bounds': {'min_lat': 37.0, 'max_lat': 37.5,
                               'min_lng': -123.0, 'max_lng': -122.5}}},
                {'entity_id': 'e2', 'jurisdiction': {
                    'bounds': {'min_lat': 37.5, 'max_lat': 38.0,
                               'min_lng': -122.5, 'max_lng': -122.0}}},
            ]
        }
        result = integration.analyze_spatial_governance_coverage(structure, region, resolution=6)
        assert result['coverage_analyzed'] is True
        assert 0.0 < result['total_coverage'] <= 1.0
        assert result['covered_cells'] <= result['total_region_cells']
        assert set(result['entity_coverage']) == {'e1', 'e2'}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
