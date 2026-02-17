"""
Unit tests for the CognitiveProcessingEngine and CognitiveState.
"""

import numpy as np
import pytest
from datetime import datetime

from geo_infer_cog.core.cognitive_engine import CognitiveState, CognitiveProcessingEngine


class TestCognitiveState:
    """Test CognitiveState data class."""

    def test_initial_state_defaults(self) -> None:
        state = CognitiveState()
        assert state.cognitive_load == 0.0
        assert state.uncertainty_level == 0.0
        assert state.decision_confidence == 0.0
        assert len(state.attention_focus) == 0
        assert len(state.working_memory) == 0

    def test_update_attention_normalizes_weights(self) -> None:
        state = CognitiveState()
        state.update_attention({'area_a': 2.0, 'area_b': 3.0})

        assert abs(state.attention_focus['area_a'] - 0.4) < 1e-6
        assert abs(state.attention_focus['area_b'] - 0.6) < 1e-6
        total = sum(state.attention_focus.values())
        assert abs(total - 1.0) < 1e-6

    def test_add_to_working_memory(self) -> None:
        state = CognitiveState()
        state.add_to_working_memory('location_1', {'lat': 40.0, 'lon': -74.0}, importance=0.9)

        assert 'location_1' in state.working_memory
        item = state.working_memory['location_1']
        assert item['value'] == {'lat': 40.0, 'lon': -74.0}
        assert item['importance'] == 0.9
        assert item['access_count'] == 0

    def test_retrieve_from_memory_increments_access(self) -> None:
        state = CognitiveState()
        state.add_to_working_memory('key_1', 'value_1')

        result = state.retrieve_from_memory('key_1')
        assert result == 'value_1'
        assert state.working_memory['key_1']['access_count'] == 1

    def test_retrieve_missing_key_returns_none(self) -> None:
        state = CognitiveState()
        assert state.retrieve_from_memory('nonexistent') is None

    def test_cognitive_load_increases_with_items(self) -> None:
        state = CognitiveState()
        for i in range(5):
            state.add_to_working_memory(f'item_{i}', f'value_{i}')

        assert state.cognitive_load > 0.0

    def test_get_memory_utilization(self) -> None:
        state = CognitiveState()
        state.add_to_working_memory('a', 1)
        state.add_to_working_memory('b', 2)
        state.retrieve_from_memory('a')

        util = state.get_memory_utilization()
        assert util['items'] == 2
        assert util['accessed_ratio'] == 0.5


class TestCognitiveProcessingEngine:
    """Test CognitiveProcessingEngine class."""

    def test_init_defaults(self) -> None:
        engine = CognitiveProcessingEngine()
        assert engine.cognitive_framework == 'bayesian_attention'
        assert engine.spatial_resolution == 'adaptive'
        assert engine.temporal_modeling == 'working_memory'
        assert engine.uncertainty_handling == 'probabilistic'

    def test_init_custom_framework(self) -> None:
        engine = CognitiveProcessingEngine(cognitive_framework='act_r')
        assert engine.cognitive_framework == 'act_r'

    def test_performance_metrics_initialized(self) -> None:
        engine = CognitiveProcessingEngine()
        metrics = engine.performance_metrics
        assert metrics['decisions_made'] == 0
        assert metrics['reasoning_chains'] == 0
        assert metrics['memory_operations'] == 0
        assert metrics['perception_updates'] == 0

    def test_get_performance_summary(self) -> None:
        engine = CognitiveProcessingEngine()
        summary = engine.get_performance_summary()

        assert summary['engine_status'] == 'active'
        assert 'cognitive_state' in summary
        assert 'performance_metrics' in summary
        assert 'model_status' in summary
        assert 'configuration' in summary
        assert summary['configuration']['cognitive_framework'] == 'bayesian_attention'

    def test_calculate_decision_confidence_with_load(self) -> None:
        engine = CognitiveProcessingEngine()
        # High cognitive load should reduce confidence
        engine.state.cognitive_load = 0.8
        alternative = {'confidence': 0.9}
        confidence = engine._calculate_decision_confidence(alternative)
        assert confidence < 0.9
        assert confidence > 0.0

    def test_estimate_cognitive_load_returns_bounded(self) -> None:
        engine = CognitiveProcessingEngine()
        alternative = {
            'geometry': {'coordinates': list(range(200))},
            'attributes': {f'attr_{i}': i for i in range(20)}
        }
        load = engine._estimate_cognitive_load(alternative)
        assert 0.0 <= load <= 1.0

    def test_recommend_action_thresholds(self) -> None:
        engine = CognitiveProcessingEngine()

        strong = engine._recommend_action(
            {'confidence': 0.9},
            {'reasoning_path': ['a', 'b', 'c', 'd']}
        )
        assert strong == 'strong_recommendation'

        weak = engine._recommend_action(
            {'confidence': 0.45},
            {'reasoning_path': []}
        )
        assert weak == 'weak_recommendation'

        further = engine._recommend_action(
            {'confidence': 0.2},
            {'reasoning_path': []}
        )
        assert further == 'requires_further_analysis'
