"""
Unit tests for orchestrator functionality.
"""

import pytest
import asyncio
from geo_infer_ops.core.orchestrator import Orchestrator, TaskStatus


class TestOrchestrator:
    """Test Orchestrator class."""

    @pytest.fixture
    def orchestrator(self) -> Orchestrator:
        """Create an orchestrator instance."""
        return Orchestrator(max_concurrent_tasks=5)

    def test_add_task(self, orchestrator: Orchestrator) -> None:
        """Test adding tasks."""

        def simple_task():
            return "result"

        task_id = orchestrator.add_task(
            name="test_task",
            func=simple_task,
        )

        assert task_id in orchestrator.tasks
        assert orchestrator.tasks[task_id].name == "test_task"

    def test_task_dependencies(self, orchestrator: Orchestrator) -> None:
        """Test task with dependencies."""

        def task1():
            return "task1_result"

        def task2():
            return "task2_result"

        task1_id = orchestrator.add_task(name="task1", func=task1)
        task2_id = orchestrator.add_task(
            name="task2", func=task2, dependencies=[task1_id]
        )

        assert task2_id in orchestrator.tasks
        assert orchestrator.tasks[task2_id].dependencies == [task1_id]

    def test_execute_workflow(self, orchestrator: Orchestrator) -> None:
        """Test workflow execution."""
        results = []

        def task1():
            results.append("task1")
            return "task1_result"

        def task2():
            results.append("task2")
            return "task2_result"

        orchestrator.add_task(name="task1", func=task1)
        orchestrator.add_task(name="task2", func=task2)

        workflow_result = asyncio.run(orchestrator.execute_workflow())

        assert workflow_result["completed_tasks"] == 2
        assert "task1" in results
        assert "task2" in results

    def test_execute_workflow_with_dependencies(
        self, orchestrator: Orchestrator
    ) -> None:
        """Test workflow execution with dependencies."""
        execution_order = []

        def task1():
            execution_order.append(1)
            return "task1_result"

        def task2():
            execution_order.append(2)
            return "task2_result"

        task1_id = orchestrator.add_task(name="task1", func=task1)
        orchestrator.add_task(name="task2", func=task2, dependencies=[task1_id])

        asyncio.run(orchestrator.execute_workflow())

        # Task1 should execute before task2
        assert execution_order == [1, 2]

    def test_get_task_status(self, orchestrator: Orchestrator) -> None:
        """Test getting task status."""

        def simple_task():
            return "result"

        task_id = orchestrator.add_task(name="test_task", func=simple_task)

        status = orchestrator.get_task_status(task_id)

        assert status is not None
        assert status["name"] == "test_task"
        assert status["status"] == TaskStatus.PENDING.value

    def test_get_workflow_status(self, orchestrator: Orchestrator) -> None:
        """Test getting workflow status."""

        def task1():
            return "result1"

        def task2():
            return "result2"

        orchestrator.add_task(name="task1", func=task1)
        orchestrator.add_task(name="task2", func=task2)

        status = orchestrator.get_workflow_status()

        assert status["total_tasks"] == 2
        assert "status_counts" in status
        assert "tasks" in status


class TestOrchestratorRetryAndDependencySemantics:
    """Focused tests for retry and dependency handling."""

    @pytest.fixture
    def orchestrator(self) -> Orchestrator:
        return Orchestrator(max_concurrent_tasks=5, retry_delay_seconds=0)

    def test_retry_until_success(self, orchestrator: Orchestrator) -> None:
        """A flaky task is retried and completes after transient failures."""
        attempts = {"count": 0}

        def flaky() -> str:
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise RuntimeError("transient failure")
            return "recovered"

        task_id = orchestrator.add_task(name="flaky", func=flaky, max_retries=3)
        result = asyncio.run(orchestrator.execute_workflow())

        assert result["completed_tasks"] == 1
        task = orchestrator.tasks[task_id]
        assert task.status == TaskStatus.COMPLETED
        assert task.retry_count == 2
        assert task.result == "recovered"

    def test_retry_exhaustion_marks_failed(self, orchestrator: Orchestrator) -> None:
        """A permanently failing task exhausts retries and is marked FAILED."""
        attempts = {"count": 0}

        def always_fails() -> None:
            attempts["count"] += 1
            raise RuntimeError("permanent failure")

        task_id = orchestrator.add_task(
            name="failing", func=always_fails, max_retries=2
        )
        result = asyncio.run(orchestrator.execute_workflow())

        assert result["failed_tasks"] == 1
        task = orchestrator.tasks[task_id]
        assert task.status == TaskStatus.FAILED
        assert attempts["count"] == 3  # initial attempt + 2 retries
        assert "permanent failure" in (task.error or "")

    def test_failed_dependency_deadlocks_dependent(
        self, orchestrator: Orchestrator
    ) -> None:
        """A task depending on a permanently failed task is marked FAILED."""
        def always_fails() -> None:
            raise RuntimeError("upstream failure")

        def dependent() -> str:
            return "never runs"

        failing_id = orchestrator.add_task(
            name="failing", func=always_fails, max_retries=0
        )
        dependent_id = orchestrator.add_task(
            name="dependent", func=dependent, dependencies=[failing_id]
        )
        result = asyncio.run(orchestrator.execute_workflow())

        assert result["failed_tasks"] >= 1
        assert orchestrator.tasks[failing_id].status == TaskStatus.FAILED
        dependent = orchestrator.tasks[dependent_id]
        assert dependent.status == TaskStatus.FAILED
        assert "deadlock" in (dependent.error or "")

    def test_invalid_dependency_raises(self, orchestrator: Orchestrator) -> None:
        """A dependency referencing an unknown task id aborts the workflow."""
        orchestrator.add_task(
            name="orphan", func=lambda: "x", dependencies=["missing-task"]
        )
        with pytest.raises(ValueError, match="Invalid task dependencies"):
            asyncio.run(orchestrator.execute_workflow())

    def test_workflow_counters_count_each_task_once(
        self, orchestrator: Orchestrator
    ) -> None:
        """Completed tasks are counted once even across multiple scheduling waves."""

        def first() -> str:
            return "first"

        def second() -> str:
            return "second"

        first_id = orchestrator.add_task(name="first", func=first)
        orchestrator.add_task(name="second", func=second, dependencies=[first_id])

        result = asyncio.run(orchestrator.execute_workflow())

        assert result["completed_tasks"] == 2
        assert result["failed_tasks"] == 0
