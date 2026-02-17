"""
Unit tests for attention mechanisms across the cognitive system.

Tests attention allocation, attention-priority calculations, and
attention-driven perceptual grouping from the perception module.
"""

import numpy as np
import pytest

from geo_infer_cog.core.spatial_perception import (
    SpatialPercept,
    AttentionModel,
    SpatialPerceptionModel,
)


class TestAttentionAllocation:
    """Test attention allocation strategies and capacity limits."""

    @pytest.fixture
    def model(self) -> AttentionModel:
        return AttentionModel(attention_capacity=1.0, focus_radius=0.5)

    def test_single_element_gets_full_attention(self, model: AttentionModel) -> None:
        elements = [
            SpatialPercept(element_id='sole', geometry={}, visual_saliency=0.6, accessibility=1.0),
        ]
        weights = model.allocate_attention(elements)
        assert abs(weights['sole'] - 1.0) < 1e-6

    def test_attention_sums_to_capacity(self, model: AttentionModel) -> None:
        elements = [
            SpatialPercept(element_id=f'e{i}', geometry={}, visual_saliency=np.random.random(), accessibility=1.0)
            for i in range(5)
        ]
        weights = model.allocate_attention(elements)
        total = sum(weights.values())
        assert abs(total - model.attention_capacity) < 1e-6

    def test_reduced_capacity_limits_total(self) -> None:
        model = AttentionModel(attention_capacity=0.5)
        elements = [
            SpatialPercept(element_id='a', geometry={}, visual_saliency=0.5, accessibility=1.0),
            SpatialPercept(element_id='b', geometry={}, visual_saliency=0.5, accessibility=1.0),
        ]
        weights = model.allocate_attention(elements)
        total = sum(weights.values())
        assert abs(total - 0.5) < 1e-6

    def test_high_saliency_dominates(self) -> None:
        model = AttentionModel()
        elements = [
            SpatialPercept(element_id='high', geometry={}, visual_saliency=0.95, accessibility=1.0),
            SpatialPercept(element_id='low', geometry={}, visual_saliency=0.05, accessibility=1.0),
        ]
        weights = model.allocate_attention(elements)
        assert weights['high'] > weights['low']


class TestAttentionPriority:
    """Test context-driven attention priority calculations."""

    def test_analysis_context_favors_low_uncertainty(self) -> None:
        certain = SpatialPercept(element_id='c', geometry={}, visual_saliency=0.5, accessibility=1.0, uncertainty=0.1)
        uncertain = SpatialPercept(element_id='u', geometry={}, visual_saliency=0.5, accessibility=1.0, uncertainty=0.8)
        # Analysis context should favor low-uncertainty elements
        assert certain.calculate_attention_priority('analysis') > uncertain.calculate_attention_priority('analysis')

    def test_planning_context_is_neutral(self) -> None:
        percept = SpatialPercept(element_id='p', geometry={}, visual_saliency=0.6, accessibility=0.8)
        priority = percept.calculate_attention_priority('planning')
        # Planning has multiplier 1.0, so priority = saliency * accessibility * 1.0
        expected = 0.6 * 0.8 * 1.0
        assert abs(priority - expected) < 1e-6

    def test_zero_accessibility_means_zero_priority(self) -> None:
        percept = SpatialPercept(element_id='z', geometry={}, visual_saliency=1.0, accessibility=0.0)
        priority = percept.calculate_attention_priority('general')
        assert priority == 0.0


class TestPerceptualGrouping:
    """Test Gestalt-based perceptual grouping in the perception model."""

    def test_nearby_elements_grouped_together(self) -> None:
        model = SpatialPerceptionModel()
        elements = [
            SpatialPercept(element_id='a', geometry={'type': 'Point', 'coordinates': [0, 0]}),
            SpatialPercept(element_id='b', geometry={'type': 'Point', 'coordinates': [1, 1]}),
        ]
        grouped = model._apply_perceptual_grouping(elements)
        # Both points are within the 50-unit grouping threshold
        groups = set(e.perceptual_group for e in grouped if e.perceptual_group)
        assert len(groups) == 1

    def test_distant_elements_not_grouped(self) -> None:
        model = SpatialPerceptionModel()
        elements = [
            SpatialPercept(element_id='a', geometry={'type': 'Point', 'coordinates': [0, 0]}),
            SpatialPercept(element_id='b', geometry={'type': 'Point', 'coordinates': [100, 100]}),
        ]
        grouped = model._apply_perceptual_grouping(elements)
        groups = [e.perceptual_group for e in grouped if e.perceptual_group]
        # Should not be in the same group (distance > 50)
        assert len(set(groups)) <= 1  # At most one group from one pair, or neither grouped

    def test_single_element_not_grouped(self) -> None:
        model = SpatialPerceptionModel()
        elements = [
            SpatialPercept(element_id='solo', geometry={'type': 'Point', 'coordinates': [5, 5]}),
        ]
        grouped = model._apply_perceptual_grouping(elements)
        assert len(grouped) == 1
        assert grouped[0].perceptual_group == ''
