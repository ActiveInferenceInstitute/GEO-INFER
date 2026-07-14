"""Integration coverage for example orchestration contracts."""

from geo_infer_examples.core.module_orchestrator import ExecutionStrategy


def test_example_workflow_strategy_is_public_and_serializable() -> None:
    """Expose the sequential strategy used by minimal example workflows."""
    assert ExecutionStrategy.SEQUENTIAL.value == "sequential"
    assert ExecutionStrategy("parallel") is ExecutionStrategy.PARALLEL
