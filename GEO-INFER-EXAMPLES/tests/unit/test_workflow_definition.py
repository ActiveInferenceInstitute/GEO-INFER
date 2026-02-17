"""Tests for WorkflowDefinition, ExecutionContext, and IntegrationPatterns."""

import pytest
import json
import tempfile
from pathlib import Path

from geo_infer_examples.models.integration_models import (
    WorkflowDefinition,
    WorkflowStep,
    ExecutionContext,
    IntegrationPatterns,
    save_workflow_to_file,
    load_workflow_from_file,
)


def _make_workflow(wf_id: str = "test_wf", steps: int = 3) -> WorkflowDefinition:
    """Helper to build a simple sequential workflow."""
    step_list = []
    for i in range(steps):
        deps = [f"step_{i - 1}"] if i > 0 else []
        step_list.append(
            WorkflowStep(
                name=f"step_{i}",
                module=f"MOD_{i}",
                endpoint=f"/run/{i}",
                dependencies=deps,
            )
        )
    return WorkflowDefinition(
        id=wf_id,
        name="Test Workflow",
        description="A test workflow",
        steps=step_list,
        tags=["test"],
    )


class TestWorkflowDefinition:
    """Tests for WorkflowDefinition dataclass."""

    def test_create_defaults(self):
        wf = _make_workflow()
        assert wf.execution_strategy == "sequential"
        assert wf.version == "1.0.0"
        assert wf.max_iterations is None
        assert wf.convergence_threshold is None
        assert wf.tags == ["test"]

    def test_to_dict(self):
        wf = _make_workflow()
        d = wf.to_dict()
        assert d["id"] == "test_wf"
        assert len(d["steps"]) == 3
        assert d["steps"][0]["name"] == "step_0"
        assert d["execution_strategy"] == "sequential"

    def test_from_dict_roundtrip(self):
        wf = _make_workflow(wf_id="roundtrip", steps=4)
        wf.max_iterations = 10
        wf.convergence_threshold = 0.01
        d = wf.to_dict()
        restored = WorkflowDefinition.from_dict(d)
        assert restored.id == "roundtrip"
        assert len(restored.steps) == 4
        assert restored.max_iterations == 10
        assert restored.convergence_threshold == 0.01

    def test_copy(self):
        wf = _make_workflow()
        copied = wf.copy()
        assert copied.id == wf.id
        assert copied is not wf
        assert copied.steps is not wf.steps
        copied.steps.append(
            WorkflowStep(name="extra", module="X", endpoint="/x")
        )
        assert len(copied.steps) == 4
        assert len(wf.steps) == 3

    def test_metadata_field(self):
        wf = _make_workflow()
        wf.metadata["author"] = "test_suite"
        d = wf.to_dict()
        assert d["metadata"]["author"] == "test_suite"

    def test_feedback_loop_fields(self):
        wf = WorkflowDefinition(
            id="fb",
            name="Feedback",
            description="Feedback workflow",
            steps=[
                WorkflowStep(
                    name="observe",
                    module="ACT",
                    endpoint="/observe",
                    feedback_mapping={"prior": "posterior"},
                ),
            ],
            execution_strategy="feedback_loop",
            max_iterations=50,
            convergence_threshold=0.005,
        )
        assert wf.execution_strategy == "feedback_loop"
        assert wf.max_iterations == 50
        assert wf.steps[0].feedback_mapping == {"prior": "posterior"}


class TestExecutionContext:
    """Tests for ExecutionContext dataclass."""

    def test_defaults(self):
        ctx = ExecutionContext()
        assert ctx.user_id is None
        assert ctx.priority == 5
        assert ctx.resilience_mode is False
        assert ctx.debug_mode is False
        assert ctx.environment == "production"
        assert ctx.tags == []

    def test_custom_values(self):
        ctx = ExecutionContext(
            user_id="u123",
            session_id="s456",
            priority=9,
            resilience_mode=True,
            debug_mode=True,
            environment="staging",
            custom_config={"gpu": True},
            tags=["high_priority"],
        )
        assert ctx.user_id == "u123"
        assert ctx.priority == 9
        assert ctx.custom_config["gpu"] is True
        assert "high_priority" in ctx.tags


class TestIntegrationPatterns:
    """Tests for pre-built workflow factory methods."""

    def test_health_surveillance_workflow(self):
        wf = IntegrationPatterns.create_health_surveillance_workflow()
        assert wf.id == "health_surveillance_standard"
        assert wf.execution_strategy == "sequential"
        assert len(wf.steps) == 7
        step_names = [s.name for s in wf.steps]
        assert "data_ingestion" in step_names
        assert "outbreak_detection" in step_names
        assert "alert_generation" in step_names

    def test_health_surveillance_dependencies(self):
        wf = IntegrationPatterns.create_health_surveillance_workflow()
        first_step = wf.steps[0]
        assert first_step.dependencies == []
        last_step = wf.steps[-1]
        assert len(last_step.dependencies) >= 1

    def test_health_surveillance_optional_step(self):
        wf = IntegrationPatterns.create_health_surveillance_workflow()
        risk_step = [s for s in wf.steps if s.name == "risk_assessment"][0]
        assert risk_step.optional is True

    def test_precision_agriculture_workflow(self):
        wf = IntegrationPatterns.create_precision_agriculture_workflow()
        assert wf.id == "precision_agriculture_monitoring"
        assert wf.execution_strategy == "parallel"
        assert len(wf.steps) == 7
        step_names = [s.name for s in wf.steps]
        assert "sensor_data_collection" in step_names
        assert "recommendations" in step_names

    def test_precision_agriculture_parallel_roots(self):
        wf = IntegrationPatterns.create_precision_agriculture_workflow()
        roots = [s for s in wf.steps if len(s.dependencies) == 0]
        assert len(roots) == 2  # sensor + satellite are independent

    def test_active_inference_workflow(self):
        wf = IntegrationPatterns.create_active_inference_workflow()
        assert wf.id == "active_inference_adaptive"
        assert wf.execution_strategy == "feedback_loop"
        assert wf.max_iterations == 10
        assert wf.convergence_threshold == 0.001

    def test_active_inference_events(self):
        wf = IntegrationPatterns.create_active_inference_workflow()
        belief_step = [s for s in wf.steps if s.name == "belief_update"][0]
        assert "beliefs_updated" in belief_step.emits_events
        assert belief_step.feedback_mapping is not None

    def test_active_inference_tags(self):
        wf = IntegrationPatterns.create_active_inference_workflow()
        assert "active_inference" in wf.tags
        assert "feedback" in wf.tags


class TestWorkflowFileIO:
    """Tests for save_workflow_to_file and load_workflow_from_file."""

    def test_save_and_load_json(self):
        wf = _make_workflow(wf_id="json_io")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        save_workflow_to_file(wf, path, format="json")
        loaded = load_workflow_from_file(path)
        assert loaded.id == "json_io"
        assert len(loaded.steps) == 3

    def test_save_and_load_yaml(self):
        wf = _make_workflow(wf_id="yaml_io")
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            path = f.name
        save_workflow_to_file(wf, path, format="yaml")
        loaded = load_workflow_from_file(path)
        assert loaded.id == "yaml_io"
        assert len(loaded.steps) == 3

    def test_unsupported_format_save_raises(self):
        wf = _make_workflow()
        with pytest.raises(ValueError, match="Unsupported format"):
            save_workflow_to_file(wf, "/tmp/test.txt", format="txt")

    def test_unsupported_format_load_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("data")
            path = f.name
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_workflow_from_file(path)
