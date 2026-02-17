"""
Unit tests for spatial reasoning: SpatialRelation, ReasoningStep, SpatialReasoningEngine.
"""

import numpy as np
import pytest

from geo_infer_cog.core.spatial_reasoning import (
    SpatialRelation,
    ReasoningStep,
    SpatialReasoningEngine,
)


class TestSpatialRelation:
    """Test SpatialRelation data class."""

    def test_defaults(self) -> None:
        rel = SpatialRelation(
            source_region='A', target_region='B', relation_type='disconnected'
        )
        assert rel.confidence == 1.0
        assert rel.reasoning_path == []

    def test_is_consistent_with_same_pair(self) -> None:
        rel1 = SpatialRelation(source_region='A', target_region='B', relation_type='disconnected')
        rel2 = SpatialRelation(source_region='B', target_region='A', relation_type='disconnected')
        assert rel1.is_consistent_with(rel2) is True

    def test_inconsistent_relations(self) -> None:
        rel1 = SpatialRelation(source_region='A', target_region='B', relation_type='disconnected')
        rel2 = SpatialRelation(source_region='B', target_region='A', relation_type='equal')
        assert rel1.is_consistent_with(rel2) is False

    def test_no_conflict_unrelated_pair(self) -> None:
        rel1 = SpatialRelation(source_region='A', target_region='B', relation_type='disconnected')
        rel2 = SpatialRelation(source_region='C', target_region='D', relation_type='equal')
        assert rel1.is_consistent_with(rel2) is True


class TestReasoningStep:
    """Test ReasoningStep class."""

    def test_step_fields(self) -> None:
        step = ReasoningStep(
            step_id='s1',
            operation='compose',
            input_premises=['p1', 'p2'],
            conclusion='c1',
            confidence=0.9,
            explanation='Test explanation',
        )
        assert step.step_id == 's1'
        assert step.operation == 'compose'
        assert len(step.input_premises) == 2
        assert step.confidence == 0.9


class TestSpatialReasoningEngine:
    """Test SpatialReasoningEngine class."""

    def test_init_defaults(self) -> None:
        engine = SpatialReasoningEngine()
        assert engine.reasoning_type == 'qualitative_spatial'
        assert engine.uncertainty_method == 'probabilistic'

    def test_knowledge_base_initialized(self) -> None:
        engine = SpatialReasoningEngine()
        kb = engine.spatial_knowledge_base
        assert 'topological_relations' in kb
        assert 'directional_relations' in kb
        assert 'distance_relations' in kb
        assert 'disconnected' in kb['topological_relations']
        assert 'north' in kb['directional_relations']

    def test_determine_topological_equal(self) -> None:
        engine = SpatialReasoningEngine()
        bbox = (0.0, 0.0, 1.0, 1.0)
        result = engine._determine_topological_relation(bbox, bbox)
        assert result == 'equal'

    def test_determine_topological_disconnected(self) -> None:
        engine = SpatialReasoningEngine()
        bbox1 = (0.0, 0.0, 1.0, 1.0)
        bbox2 = (5.0, 5.0, 6.0, 6.0)
        result = engine._determine_topological_relation(bbox1, bbox2)
        assert result == 'disconnected'

    def test_determine_topological_overlapping(self) -> None:
        engine = SpatialReasoningEngine()
        bbox1 = (0.0, 0.0, 2.0, 2.0)
        bbox2 = (1.0, 1.0, 3.0, 3.0)
        result = engine._determine_topological_relation(bbox1, bbox2)
        assert result == 'partially_overlapping'

    def test_determine_topological_nontangential_proper_part(self) -> None:
        engine = SpatialReasoningEngine()
        inner = (0.5, 0.5, 1.5, 1.5)
        outer = (0.0, 0.0, 2.0, 2.0)
        result = engine._determine_topological_relation(inner, outer)
        assert result == 'non_tangential_proper_part'

    def test_compose_relations_chain(self) -> None:
        engine = SpatialReasoningEngine()
        rel1 = SpatialRelation(source_region='A', target_region='B', relation_type='disconnected')
        rel2 = SpatialRelation(source_region='B', target_region='C', relation_type='disconnected')
        composed = engine._compose_relations(rel1, rel2)
        assert composed is not None
        assert composed.source_region == 'A'
        assert composed.target_region == 'C'
        assert composed.relation_type == 'disconnected'

    def test_compose_relations_no_chain_returns_none(self) -> None:
        engine = SpatialReasoningEngine()
        rel1 = SpatialRelation(source_region='A', target_region='B', relation_type='disconnected')
        rel2 = SpatialRelation(source_region='C', target_region='D', relation_type='equal')
        assert engine._compose_relations(rel1, rel2) is None

    def test_get_alternative_relations(self) -> None:
        engine = SpatialReasoningEngine()
        alts = engine._get_alternative_relations('disconnected')
        assert 'externally_connected' in alts

    def test_get_status(self) -> None:
        engine = SpatialReasoningEngine()
        status = engine.get_status()
        assert status['engine_type'] == 'spatial_reasoning'
        assert status['reasoning_type'] == 'qualitative_spatial'
        assert status['status'] == 'active'

    def test_calculate_overall_confidence_empty(self) -> None:
        engine = SpatialReasoningEngine()
        assert engine._calculate_overall_confidence([]) == 0.0

    def test_validate_reasoning_chain_no_issues(self) -> None:
        engine = SpatialReasoningEngine()
        conclusions = [
            SpatialRelation(source_region='A', target_region='B', relation_type='disconnected', confidence=0.9),
        ]
        result = engine._validate_reasoning_chain(conclusions, 'chain_1')
        assert result['valid'] is True
        assert abs(result['confidence'] - 0.9) < 1e-6
