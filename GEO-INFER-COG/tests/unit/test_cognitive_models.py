"""
Unit tests for CognitiveMap and SpatialKnowledgeGraph.
"""

import numpy as np
import pytest

from geo_infer_cog.models.cognitive_models import (
    SpatialNode,
    SpatialEdge,
    CognitiveMap,
    SpatialKnowledgeGraph,
)
from geo_infer_cog.models.user_profiles import UserCognitiveProfile


def _make_profile(**overrides) -> UserCognitiveProfile:
    defaults = dict(
        user_id='user_1',
        spatial_expertise=0.5,
        cognitive_load_preference='moderate',
        cognitive_style='balanced',
        spatial_reasoning_style='balanced',
    )
    defaults.update(overrides)
    return UserCognitiveProfile(**defaults)


class TestSpatialNode:
    """Test SpatialNode data class."""

    def test_cognitive_weight_default(self) -> None:
        node = SpatialNode(node_id='n1', node_type='landmark', saliency=0.8, accessibility=0.9)
        weight = node.calculate_cognitive_weight()
        assert abs(weight - 0.8 * 0.9) < 1e-6

    def test_cognitive_weight_with_profile(self) -> None:
        node = SpatialNode(node_id='n1', node_type='landmark', saliency=0.5, accessibility=1.0)
        profile = _make_profile(spatial_expertise=0.8)
        weight_with = node.calculate_cognitive_weight(profile)
        weight_without = node.calculate_cognitive_weight()
        assert weight_with > weight_without


class TestSpatialEdge:
    """Test SpatialEdge data class."""

    def test_effective_strength_default(self) -> None:
        edge = SpatialEdge(
            edge_id='e1', source_node='a', target_node='b',
            relation_type='topological', strength=0.8, confidence=0.9,
        )
        assert abs(edge.get_effective_strength() - 0.8 * 0.9) < 1e-6

    def test_effective_strength_qualitative_user_boosts_topological(self) -> None:
        edge = SpatialEdge(
            edge_id='e1', source_node='a', target_node='b',
            relation_type='topological', strength=0.5, confidence=1.0,
        )
        profile = _make_profile(spatial_reasoning_style='qualitative')
        strength = edge.get_effective_strength(profile)
        assert strength > 0.5


class TestCognitiveMap:
    """Test CognitiveMap class."""

    @pytest.fixture
    def cmap(self) -> CognitiveMap:
        return CognitiveMap(
            map_id='test_map',
            spatial_bounds={'min_lat': 0, 'max_lat': 10, 'min_lon': 0, 'max_lon': 10},
        )

    def test_add_landmark(self, cmap: CognitiveMap) -> None:
        cmap.add_landmark('lm1', {'type': 'Point', 'coordinates': [5, 5]}, {'name': 'Center'}, saliency=0.9)
        assert 'lm1' in cmap.landmarks
        assert cmap.map_metrics['landmarks_count'] == 1

    def test_add_route_requires_landmarks(self, cmap: CognitiveMap) -> None:
        with pytest.raises(ValueError, match="landmarks must be added"):
            cmap.add_route('r1', 'lm_a', 'lm_b', [], {})

    def test_add_route_creates_connections(self, cmap: CognitiveMap) -> None:
        cmap.add_landmark('lm_a', {'type': 'Point', 'coordinates': [0, 0]}, {'name': 'A'})
        cmap.add_landmark('lm_b', {'type': 'Point', 'coordinates': [10, 10]}, {'name': 'B'})
        cmap.add_route('r1', 'lm_a', 'lm_b', [{'segment': 1}], {'length': 100, 'mode': 'walking'})

        assert cmap.map_metrics['routes_count'] == 1
        assert len(cmap.connections['lm_a']) == 1
        assert len(cmap.connections['lm_b']) == 1

    def test_navigation_path_between_landmarks(self, cmap: CognitiveMap) -> None:
        cmap.add_landmark('A', {'type': 'Point', 'coordinates': [0, 0]}, {'name': 'A'})
        cmap.add_landmark('B', {'type': 'Point', 'coordinates': [5, 0]}, {'name': 'B'})
        cmap.add_landmark('C', {'type': 'Point', 'coordinates': [10, 0]}, {'name': 'C'})
        cmap.add_route('r1', 'A', 'B', [{}], {'length': 50, 'mode': 'walking'})
        cmap.add_route('r2', 'B', 'C', [{}], {'length': 50, 'mode': 'walking'})

        path = cmap.get_navigation_path('A', 'C')
        assert path[0] == 'A'
        assert path[-1] == 'C'

    def test_navigation_nonexistent_landmark_empty(self, cmap: CognitiveMap) -> None:
        path = cmap.get_navigation_path('X', 'Y')
        assert path == []

    def test_cognitive_load_increases_with_complexity(self, cmap: CognitiveMap) -> None:
        for i in range(10):
            cmap.add_landmark(f'lm_{i}', {'type': 'Point', 'coordinates': [i, i]}, {'name': f'LM{i}'})
        load = cmap.calculate_cognitive_load()
        assert load > 0.0

    def test_export_to_geojson(self, cmap: CognitiveMap) -> None:
        cmap.add_landmark('lm1', {'type': 'Point', 'coordinates': [1, 2]}, {'name': 'Test'})
        geojson = cmap.export_to_geojson()
        assert geojson['type'] == 'FeatureCollection'
        assert len(geojson['features']) >= 1

    def test_get_map_statistics(self, cmap: CognitiveMap) -> None:
        cmap.add_landmark('lm1', {'type': 'Point', 'coordinates': [0, 0]}, {'name': 'A'}, saliency=0.7)
        stats = cmap.get_map_statistics()
        assert stats['map_id'] == 'test_map'
        assert stats['components']['landmarks'] == 1


class TestSpatialKnowledgeGraph:
    """Test SpatialKnowledgeGraph class."""

    @pytest.fixture
    def skg(self) -> SpatialKnowledgeGraph:
        return SpatialKnowledgeGraph(graph_id='test_kg', domain='urban')

    def test_add_entity(self, skg: SpatialKnowledgeGraph) -> None:
        skg.add_spatial_entity('park_1', 'landmark', properties={'name': 'Central Park'})
        assert 'park_1' in skg.graph
        assert skg.graph_metrics['nodes_count'] == 1

    def test_add_relationship_requires_entities(self, skg: SpatialKnowledgeGraph) -> None:
        skg.add_spatial_entity('a', 'location')
        with pytest.raises(ValueError, match="Both entities must exist"):
            skg.add_spatial_relationship('a', 'nonexistent', 'adjacent')

    def test_add_relationship_and_query(self, skg: SpatialKnowledgeGraph) -> None:
        skg.add_spatial_entity('a', 'location')
        skg.add_spatial_entity('b', 'location')
        skg.add_spatial_relationship('a', 'b', 'adjacent', {'distance': 100})

        rels = skg.query_spatial_relationships('a')
        assert len(rels) == 1
        assert rels[0]['target'] == 'b'
        assert rels[0]['relation_type'] == 'adjacent'

    def test_query_with_relation_type_filter(self, skg: SpatialKnowledgeGraph) -> None:
        skg.add_spatial_entity('a', 'location')
        skg.add_spatial_entity('b', 'location')
        skg.add_spatial_entity('c', 'location')
        skg.add_spatial_relationship('a', 'b', 'adjacent')
        skg.add_spatial_relationship('a', 'c', 'contains')

        rels = skg.query_spatial_relationships('a', relation_types=['contains'])
        assert len(rels) == 1
        assert rels[0]['relation_type'] == 'contains'

    def test_multi_hop_query(self, skg: SpatialKnowledgeGraph) -> None:
        skg.add_spatial_entity('a', 'location')
        skg.add_spatial_entity('b', 'location')
        skg.add_spatial_entity('c', 'location')
        skg.add_spatial_relationship('a', 'b', 'adjacent')
        skg.add_spatial_relationship('b', 'c', 'adjacent')

        rels = skg.query_spatial_relationships('a', max_depth=2)
        targets = [r['target'] for r in rels]
        assert 'b' in targets
        assert 'c' in targets

    def test_find_cluster_patterns(self, skg: SpatialKnowledgeGraph) -> None:
        for i in range(4):
            skg.add_spatial_entity(f'n{i}', 'location')
        skg.add_spatial_relationship('n0', 'n1', 'adjacent')
        skg.add_spatial_relationship('n1', 'n2', 'adjacent')
        skg.add_spatial_relationship('n2', 'n3', 'adjacent')
        skg.add_spatial_relationship('n3', 'n0', 'adjacent')

        patterns = skg.find_spatial_patterns(pattern_type='clusters')
        assert len(patterns) >= 1
        assert patterns[0]['size'] >= 3

    def test_get_graph_statistics(self, skg: SpatialKnowledgeGraph) -> None:
        skg.add_spatial_entity('a', 'landmark')
        skg.add_spatial_entity('b', 'region')
        skg.add_spatial_relationship('a', 'b', 'contains')

        stats = skg.get_graph_statistics()
        assert stats['nodes'] == 2
        assert stats['edges'] == 1
        assert 'landmark' in stats['entity_types']
        assert 'contains' in stats['relation_types']

    def test_import_from_geojson(self, skg: SpatialKnowledgeGraph) -> None:
        geojson = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'geometry': {'type': 'Point', 'coordinates': [0, 0]},
                    'properties': {'id': 'geo_1', 'type': 'landmark'},
                },
                {
                    'geometry': {'type': 'Point', 'coordinates': [1, 1]},
                    'properties': {'id': 'geo_2', 'type': 'location'},
                },
            ],
        }
        skg.import_from_geojson(geojson)
        assert skg.graph.number_of_nodes() == 2
