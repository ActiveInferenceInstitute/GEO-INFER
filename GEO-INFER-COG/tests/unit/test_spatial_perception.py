"""
Unit tests for spatial perception models: SpatialPercept, AttentionModel, SpatialPerceptionModel.
"""

import numpy as np
import pytest

from geo_infer_cog.core.spatial_perception import (
    SpatialPercept,
    AttentionModel,
    SpatialPerceptionModel,
)


class TestSpatialPercept:
    """Test SpatialPercept data class."""

    def test_default_values(self) -> None:
        percept = SpatialPercept(element_id='e1', geometry={'type': 'Point', 'coordinates': [0, 0]})
        assert percept.visual_saliency == 0.0
        assert percept.attention_weight == 0.0
        assert percept.scale_level == 'medium'
        assert percept.uncertainty == 0.0

    def test_attention_priority_general(self) -> None:
        percept = SpatialPercept(
            element_id='e1',
            geometry={'type': 'Point', 'coordinates': [0, 0]},
            visual_saliency=0.8,
            accessibility=1.0,
        )
        priority = percept.calculate_attention_priority('general')
        assert 0.0 <= priority <= 1.0

    def test_attention_priority_navigation_boosts_large_scale(self) -> None:
        large = SpatialPercept(
            element_id='e1',
            geometry={},
            visual_saliency=0.5,
            accessibility=1.0,
            scale_level='large',
        )
        small = SpatialPercept(
            element_id='e2',
            geometry={},
            visual_saliency=0.5,
            accessibility=1.0,
            scale_level='small',
        )
        assert large.calculate_attention_priority('navigation') > small.calculate_attention_priority('navigation')

    def test_attention_priority_search_boosts_salient(self) -> None:
        salient = SpatialPercept(element_id='e1', geometry={}, visual_saliency=0.9, accessibility=1.0)
        dull = SpatialPercept(element_id='e2', geometry={}, visual_saliency=0.3, accessibility=1.0)
        assert salient.calculate_attention_priority('search') > dull.calculate_attention_priority('search')


class TestAttentionModel:
    """Test AttentionModel class."""

    def test_init_defaults(self) -> None:
        model = AttentionModel()
        assert model.attention_capacity == 1.0
        assert model.focus_radius == 0.5

    def test_allocate_attention_empty_returns_empty(self) -> None:
        model = AttentionModel()
        assert model.allocate_attention([]) == {}

    def test_allocate_attention_normalizes(self) -> None:
        model = AttentionModel()
        elements = [
            SpatialPercept(element_id='a', geometry={}, visual_saliency=0.8, accessibility=1.0),
            SpatialPercept(element_id='b', geometry={}, visual_saliency=0.2, accessibility=1.0),
        ]
        weights = model.allocate_attention(elements)
        assert 'a' in weights
        assert 'b' in weights
        assert weights['a'] > weights['b']
        total = sum(weights.values())
        assert abs(total - 1.0) < 1e-6

    def test_allocate_attention_uniform_when_zero_priority(self) -> None:
        model = AttentionModel()
        elements = [
            SpatialPercept(element_id='a', geometry={}, visual_saliency=0.0, accessibility=0.0),
            SpatialPercept(element_id='b', geometry={}, visual_saliency=0.0, accessibility=0.0),
        ]
        weights = model.allocate_attention(elements)
        assert abs(weights['a'] - weights['b']) < 1e-6


class TestSpatialPerceptionModel:
    """Test SpatialPerceptionModel class."""

    def test_init_defaults(self) -> None:
        model = SpatialPerceptionModel()
        assert model.framework == 'bayesian_attention'
        assert model.resolution == 'adaptive'

    def test_get_status(self) -> None:
        model = SpatialPerceptionModel()
        status = model.get_status()
        assert status['model_type'] == 'spatial_perception'
        assert status['framework'] == 'bayesian_attention'
        assert status['status'] == 'active'

    def test_polygon_area_shoelace(self) -> None:
        model = SpatialPerceptionModel()
        # Unit square: area = 1.0
        coords = [[0, 0], [1, 0], [1, 1], [0, 1]]
        area = model._calculate_polygon_area(coords)
        assert abs(area - 1.0) < 1e-6

    def test_line_length(self) -> None:
        model = SpatialPerceptionModel()
        coords = [[0.0, 0.0], [3.0, 4.0]]
        length = model._calculate_line_length(coords)
        assert abs(length - 5.0) < 1e-6

    def test_centroid_point(self) -> None:
        model = SpatialPerceptionModel()
        geom = {'type': 'Point', 'coordinates': [10.0, 20.0]}
        centroid = model._calculate_centroid(geom)
        assert centroid == (10.0, 20.0)

    def test_determine_scale_level(self) -> None:
        model = SpatialPerceptionModel()
        small = model._determine_scale_level({'type': 'Point', 'coordinates': [0, 0]})
        assert small == 'small'

    def test_process_spatial_input_returns_expected_keys(self) -> None:
        model = SpatialPerceptionModel()
        spatial_data = {
            'geometries': [
                {'type': 'Point', 'coordinates': [0, 0]},
                {'type': 'Point', 'coordinates': [1, 1]},
            ]
        }
        result = model.process_spatial_input(spatial_data)
        assert 'spatial_elements' in result
        assert 'attention_weights' in result
        assert 'perceptual_insights' in result
        assert len(result['spatial_elements']) == 2

    def test_update_model_returns_results(self) -> None:
        model = SpatialPerceptionModel()
        result = model.update_model({'perception_feedback': {'saliency_accuracy': 0.9}})
        assert 'parameters_updated' in result
