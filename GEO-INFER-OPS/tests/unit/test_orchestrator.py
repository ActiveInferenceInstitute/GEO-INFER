"""
Unit tests for orchestrator functionality.
"""

import pytest
import asyncio
from geo_infer_ops.core.orchestrator import Orchestrator, Task, TaskStatus


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


