"""
Tests for the IntelligentETLPipeline and TransformationEngine.
"""

import asyncio
import numpy as np
import pandas as pd
import pytest

from geo_infer_data.core.pipeline import (
    ErrorRecoveryStrategy,
    IntelligentETLPipeline,
    PipelineStatus,
    TransformationEngine,
)
from geo_infer_data.models.schemas import Transformation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# TransformationEngine
# ---------------------------------------------------------------------------


class TestTransformationEngine:
    def test_filter_transformation(self):
        engine = TransformationEngine()
        df = pd.DataFrame(
            {
                "temperature": [10, 20, 30, 40, 50],
                "humidity": [60, 70, 80, 90, 100],
            }
        )
        transform = Transformation(
            type="filter",
            parameters={"conditions": {"temperature": {"min": 20, "max": 40}}},
        )
        result = _run(engine.execute_transformation(transform, df, {}))
        assert len(result) == 3
        assert result["temperature"].min() >= 20
        assert result["temperature"].max() <= 40

    def test_transform_scale(self):
        engine = TransformationEngine()
        df = pd.DataFrame({"value": [1.0, 2.0, 3.0]})
        transform = Transformation(
            type="transform",
            parameters={"transformations": {"value": {"type": "scale", "factor": 10}}},
        )
        result = _run(engine.execute_transformation(transform, df, {}))
        assert list(result["value"]) == [10.0, 20.0, 30.0]

    def test_transform_normalize(self):
        engine = TransformationEngine()
        df = pd.DataFrame({"value": [0.0, 50.0, 100.0]})
        transform = Transformation(
            type="transform",
            parameters={"transformations": {"value": {"type": "normalize"}}},
        )
        result = _run(engine.execute_transformation(transform, df, {}))
        assert result["value"].min() == pytest.approx(0.0)
        assert result["value"].max() == pytest.approx(1.0)

    def test_aggregate_transformation(self):
        engine = TransformationEngine()
        df = pd.DataFrame(
            {
                "category": ["A", "A", "B", "B"],
                "value": [10, 20, 30, 40],
            }
        )
        transform = Transformation(
            type="aggregate",
            parameters={
                "group_by": ["category"],
                "aggregations": {"value": "sum"},
            },
        )
        result = _run(engine.execute_transformation(transform, df, {}))
        assert len(result) == 2
        row_a = result[result["category"] == "A"]
        assert row_a["value"].iloc[0] == 30

    def test_unknown_transformation_raises(self):
        engine = TransformationEngine()
        transform = Transformation(type="nonexistent", parameters={})
        with pytest.raises(ValueError, match="Unknown transformation type"):
            _run(engine.execute_transformation(transform, {}, {}))

    def test_clean_removes_duplicates_fills_values_and_filters_iqr(self):
        engine = TransformationEngine()
        data = pd.DataFrame({"value": [1.0, np.nan, 2.0, 2.0, 100.0]})
        transform = Transformation(
            type="clean",
            parameters={
                "fill_method": "interpolate",
                "outlier_method": "iqr",
                "remove_duplicates": True,
            },
        )

        result = _run(engine.execute_transformation(transform, data, {}))

        assert result["value"].notna().all()
        assert 100.0 not in result["value"].to_list()
        assert len(result) == 3

    def test_temporal_aggregate_resamples_configured_column(self):
        engine = TransformationEngine()
        data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=4, freq="30min"),
                "value": [1.0, 3.0, 5.0, 7.0],
            }
        )
        transform = Transformation(
            type="temporal_aggregate",
            parameters={
                "time_column": "timestamp",
                "frequency": "1h",
                "aggregation": {"value": "mean"},
            },
        )

        result = _run(engine.execute_transformation(transform, data, {}))

        assert result["value"].to_list() == [2.0, 6.0]


# ---------------------------------------------------------------------------
# IntelligentETLPipeline
# ---------------------------------------------------------------------------


class TestIntelligentETLPipeline:
    def test_pipeline_creation_no_config(self):
        pipeline = IntelligentETLPipeline()
        assert pipeline.pipeline is None
        assert pipeline.execution_history == []

    def test_execute_workflow_passthrough(self):
        """Without transformations, data passes through unchanged."""
        pipeline = IntelligentETLPipeline(monitoring_enabled=False)
        source_data = pd.DataFrame({"x": [1, 2, 3]})
        result = _run(
            pipeline.execute_workflow(
                source_data=source_data,
                target_storage=None,
            )
        )
        assert result["status"] == "completed"
        assert result["extracted_records"] == 3

    def test_execution_history_recorded(self):
        pipeline = IntelligentETLPipeline(monitoring_enabled=False)
        _run(
            pipeline.execute_workflow(
                source_data=pd.DataFrame({"a": [1]}),
                target_storage=None,
            )
        )
        assert len(pipeline.execution_history) == 1

    def test_get_performance_metrics_monitoring_disabled(self):
        pipeline = IntelligentETLPipeline(monitoring_enabled=False)
        metrics = pipeline.get_performance_metrics()
        assert metrics.get("monitoring_disabled") is True

    def test_load_to_mapping_stores_transformed_data(self):
        pipeline = IntelligentETLPipeline(monitoring_enabled=False)
        target = {}
        data = pd.DataFrame({"value": [1, 2]})

        result = _run(pipeline.execute_workflow(data, target))

        assert result["load_result"]["destination"] == "mapping"
        assert target["records_loaded"] == 2
        pd.testing.assert_frame_equal(target["data"], data)

    def test_identify_bottlenecks_empty(self):
        pipeline = IntelligentETLPipeline()
        bottlenecks = pipeline.identify_bottlenecks({"execution_time_seconds": 10})
        assert bottlenecks == []

    def test_identify_bottlenecks_long_execution(self):
        pipeline = IntelligentETLPipeline()
        bottlenecks = pipeline.identify_bottlenecks({"execution_time_seconds": 7200})
        assert len(bottlenecks) > 0


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestPipelineEnums:
    def test_pipeline_status_values(self):
        assert PipelineStatus.IDLE == "idle"
        assert PipelineStatus.COMPLETED == "completed"

    def test_error_recovery_strategy_values(self):
        assert ErrorRecoveryStrategy.FAIL_FAST == "fail_fast"
        assert ErrorRecoveryStrategy.INTELLIGENT_RETRY == "intelligent_retry"
