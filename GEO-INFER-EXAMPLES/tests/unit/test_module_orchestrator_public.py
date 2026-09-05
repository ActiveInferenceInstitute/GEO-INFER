"""Regression tests for the EXAMPLES module fixes: packaging, sample
workflows, guard-condition error handling, and the demo entrypoint."""

import asyncio

import pytest

import geo_infer_examples
from geo_infer_examples.core import (
    ExecutionStrategy,
    ModuleOrchestrator,
    ModuleStatus,
)
from geo_infer_examples.core.module_orchestrator import main


class TestPackageSurface:
    """The core subpackage must be importable without sys.path tricks."""

    def test_core_subpackage_importable(self):
        import geo_infer_examples.core

        assert geo_infer_examples.core.ModuleOrchestrator is ModuleOrchestrator

    def test_top_level_reexports(self):
        assert geo_infer_examples.ExecutionStrategy is ExecutionStrategy
        assert geo_infer_examples.ModuleStatus is ModuleStatus


class TestSampleWorkflows:
    """Bundled sample workflows must be registered as listable definitions."""

    def test_list_workflows_is_not_empty(self):
        orchestrator = ModuleOrchestrator()
        assert "health_surveillance_basic" in orchestrator.list_workflows()

    def test_sample_workflow_definition_is_retrievable(self):
        orchestrator = ModuleOrchestrator()
        workflow = orchestrator.get_workflow_definition("health_surveillance_basic")
        assert workflow is not None
        assert [step.name for step in workflow.steps] == [
            "data_ingestion",
            "spatial_analysis",
            "health_assessment",
        ]


class TestGuardConditionErrors:
    """Malformed guards skip the step loudly; programming errors propagate."""

    def test_missing_attribute_raises_key_error(self):
        orchestrator = ModuleOrchestrator()
        with pytest.raises(KeyError):
            orchestrator._evaluate_condition("data.missing > 0", {"count": 2})

    def test_malformed_syntax_evaluates_false(self):
        orchestrator = ModuleOrchestrator()
        assert orchestrator._evaluate_condition("data.count > ", {"count": 2}) is False


class TestDemoEntrypoint:
    """The hoisted main() must be importable and awaitable."""

    def test_main_is_importable_and_coroutine(self):
        assert asyncio.iscoroutinefunction(main)
