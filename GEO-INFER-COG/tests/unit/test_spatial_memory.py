"""
Unit tests for spatial memory: SpatialMemoryItem, MemoryConsolidation, SpatialMemoryModel.
"""

import numpy as np
import pytest
from datetime import datetime, timedelta

from geo_infer_cog.core.spatial_memory import (
    SpatialMemoryItem,
    MemoryConsolidation,
    SpatialMemoryModel,
)


class TestSpatialMemoryItem:
    """Test SpatialMemoryItem data class."""

    def test_default_values(self) -> None:
        item = SpatialMemoryItem(item_id='m1', content={'data': 1}, memory_type='working')
        assert item.importance == 1.0
        assert item.confidence == 1.0
        assert item.access_count == 0
        assert item.decay_rate == 0.1

    def test_retrieval_probability_decreases_with_decay(self) -> None:
        item = SpatialMemoryItem(
            item_id='m1',
            content={'data': 1},
            memory_type='working',
            creation_time=datetime.now() - timedelta(hours=10),
            decay_rate=0.5,
        )
        prob = item.calculate_retrieval_probability()
        # After 10 hours with decay_rate=0.5, probability should be significantly reduced
        assert prob < 1.0

    def test_update_access_increments_count(self) -> None:
        item = SpatialMemoryItem(item_id='m1', content={}, memory_type='working')
        item.update_access()
        assert item.access_count == 1
        assert item.last_access_time is not None
        assert item.importance > 1.0 - 0.01  # importance boosted

    def test_decay_memory_reduces_confidence(self) -> None:
        item = SpatialMemoryItem(
            item_id='m1',
            content={},
            memory_type='working',
            creation_time=datetime.now() - timedelta(hours=5),
            confidence=1.0,
            importance=1.0,
            decay_rate=0.3,
        )
        original_confidence = item.confidence
        item.decay_memory()
        assert item.confidence < original_confidence

    def test_fresh_item_has_high_retrieval_probability(self) -> None:
        item = SpatialMemoryItem(item_id='m1', content={}, memory_type='working')
        prob = item.calculate_retrieval_probability()
        assert prob > 0.9


class TestMemoryConsolidation:
    """Test MemoryConsolidation class."""

    def test_init_defaults(self) -> None:
        mc = MemoryConsolidation()
        assert mc.consolidation_threshold == 0.7
        assert mc.consolidation_delay == 300

    def test_consolidation_requires_threshold_and_delay(self) -> None:
        mc = MemoryConsolidation(consolidation_threshold=0.5, consolidation_delay=0)
        old_item = SpatialMemoryItem(
            item_id='m1',
            content={},
            memory_type='working',
            importance=0.8,
            creation_time=datetime.now() - timedelta(seconds=10),
        )
        ready = mc.check_for_consolidation([old_item])
        assert len(ready) == 1
        assert ready[0].memory_type == 'long_term'

    def test_low_importance_not_consolidated(self) -> None:
        mc = MemoryConsolidation(consolidation_threshold=0.9, consolidation_delay=0)
        item = SpatialMemoryItem(
            item_id='m1',
            content={},
            memory_type='working',
            importance=0.5,
            creation_time=datetime.now() - timedelta(seconds=600),
        )
        ready = mc.check_for_consolidation([item])
        assert len(ready) == 0


class TestSpatialMemoryModel:
    """Test SpatialMemoryModel class."""

    def test_init_defaults(self) -> None:
        model = SpatialMemoryModel()
        assert 'working' in model.memory_types
        assert 'long_term' in model.memory_types
        assert model.memory_capacities['working'] == 7

    def test_store_and_search(self) -> None:
        model = SpatialMemoryModel()
        item_id = model.store_spatial_memory(
            content={'type': 'spatial_element', 'name': 'test_location'},
            memory_type='working',
            importance=0.9,
        )
        assert item_id.startswith('working_')

        results = model.search_memory(
            query={'content_type': 'spatial_element'},
            memory_types=['working'],
        )
        assert len(results) >= 1
        assert results[0]['content']['name'] == 'test_location'

    def test_store_invalid_memory_type_raises(self) -> None:
        model = SpatialMemoryModel()
        with pytest.raises(ValueError, match="Unsupported memory type"):
            model.store_spatial_memory(content={}, memory_type='imaginary')

    def test_capacity_limit_removes_least_important(self) -> None:
        model = SpatialMemoryModel(config={'working_memory_capacity': 2})
        model.store_spatial_memory(content={'id': 1}, memory_type='working', importance=0.3)
        model.store_spatial_memory(content={'id': 2}, memory_type='working', importance=0.9)
        # Third item should trigger removal of least important
        model.store_spatial_memory(content={'id': 3}, memory_type='working', importance=0.8)

        working_items = model.memory_storage['working']
        assert len(working_items) <= 2

    def test_get_memory_statistics(self) -> None:
        model = SpatialMemoryModel()
        model.store_spatial_memory(content={'a': 1}, memory_type='working')
        stats = model.get_memory_statistics()

        assert 'memory_utilization' in stats
        assert 'working' in stats['memory_utilization']
        assert stats['memory_utilization']['working']['used'] >= 1

    def test_get_status(self) -> None:
        model = SpatialMemoryModel()
        status = model.get_status()
        assert status['model_type'] == 'spatial_memory'
        assert status['status'] == 'active'
        assert 'working' in status['memory_utilization']

    def test_search_with_importance_threshold(self) -> None:
        model = SpatialMemoryModel()
        model.store_spatial_memory(content={'type': 'low'}, memory_type='working', importance=0.2)
        model.store_spatial_memory(content={'type': 'high'}, memory_type='working', importance=0.9)

        results = model.search_memory(query={'min_importance': 0.5})
        # Only the high-importance item should match
        assert all(r['importance'] >= 0.5 for r in results)

    def test_export_memory_knowledge_graph(self) -> None:
        model = SpatialMemoryModel()
        model.store_spatial_memory(
            content={'type': 'spatial_element'},
            memory_type='working',
        )
        kg = model.export_memory_knowledge_graph()
        assert 'nodes' in kg
        assert 'edges' in kg
        assert kg['metadata']['total_items'] >= 1
