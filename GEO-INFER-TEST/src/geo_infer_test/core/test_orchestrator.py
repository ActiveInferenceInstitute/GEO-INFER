"""
GEO-INFER-TEST Test Orchestrator.

Coordinates test execution across modules, resolves inter-module
dependencies, and manages named test suites.
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class TestSuiteDefinition:
    """Definition of a named test suite."""

    name: str
    description: str
    test_patterns: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    markers: List[str] = field(default_factory=list)
    timeout_seconds: int = 300


class TestSuiteManager:
    """
    Manages named test suites: register, list, retrieve, and combine.
    """

    # Built-in suite definitions
    _BUILTIN_SUITES = {
        "unit": TestSuiteDefinition(
            name="unit",
            description="Unit tests for individual components",
            test_patterns=["tests/unit/test_*.py"],
            markers=["unit"],
        ),
        "integration": TestSuiteDefinition(
            name="integration",
            description="Cross-module integration tests",
            test_patterns=["tests/integration/test_*.py"],
            markers=["integration"],
        ),
        "performance": TestSuiteDefinition(
            name="performance",
            description="Performance and benchmark tests",
            test_patterns=["tests/performance/test_*.py"],
            markers=["benchmark", "performance"],
            timeout_seconds=600,
        ),
        "smoke": TestSuiteDefinition(
            name="smoke",
            description="Quick smoke tests for basic sanity",
            test_patterns=["tests/unit/test_*.py"],
            markers=["smoke"],
            timeout_seconds=60,
        ),
    }

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._suites: Dict[str, TestSuiteDefinition] = dict(self._BUILTIN_SUITES)

    def register_suite(self, suite: TestSuiteDefinition) -> None:
        """Register or overwrite a named test suite."""
        self._suites[suite.name] = suite
        self.logger.info("Registered suite: %s", suite.name)

    def get_suite(self, name: str) -> Optional[TestSuiteDefinition]:
        return self._suites.get(name)

    def list_suites(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": s.name,
                "description": s.description,
                "patterns": s.test_patterns,
                "modules": s.modules,
                "markers": s.markers,
                "timeout_seconds": s.timeout_seconds,
            }
            for s in self._suites.values()
        ]

    def combine_suites(self, names: List[str]) -> TestSuiteDefinition:
        """Create a combined suite from multiple named suites."""
        patterns: List[str] = []
        modules_set: Set[str] = set()
        markers: List[str] = []
        max_timeout = 300

        for name in names:
            suite = self._suites.get(name)
            if suite is None:
                self.logger.warning("Suite '%s' not found, skipping", name)
                continue
            patterns.extend(suite.test_patterns)
            modules_set.update(suite.modules)
            markers.extend(suite.markers)
            max_timeout = max(max_timeout, suite.timeout_seconds)

        return TestSuiteDefinition(
            name="combined_" + "_".join(names),
            description=f"Combined suite from: {', '.join(names)}",
            test_patterns=list(dict.fromkeys(patterns)),  # deduplicate, keep order
            modules=sorted(modules_set),
            markers=list(dict.fromkeys(markers)),
            timeout_seconds=max_timeout,
        )


class TestOrchestrator:
    """
    Coordinates test execution order based on module dependencies,
    priority levels, and suite definitions.
    """

    # Default dependency graph (module → list of modules it depends on)
    DEFAULT_DEPENDENCIES: Dict[str, List[str]] = {
        "TEST": [],
        "LOG": [],
        "MATH": [],
        "DATA": ["LOG"],
        "SPACE": ["MATH", "DATA"],
        "TIME": ["MATH", "DATA"],
        "BAYES": ["MATH"],
        "AI": ["MATH", "DATA", "BAYES"],
        "ACT": ["BAYES", "MATH"],
        "AGENT": ["ACT", "AI"],
        "ANT": ["AGENT"],
        "SIM": ["SPACE", "TIME", "AI"],
        "API": ["DATA", "SEC"],
        "APP": ["API"],
        "SEC": ["LOG"],
        "OPS": ["LOG", "API"],
        "IOT": ["SPACE", "TIME", "DATA"],
        "HEALTH": ["SPACE", "TIME", "AI"],
        "AG": ["SPACE", "TIME", "AI"],
        "ECON": ["MATH", "DATA"],
        "RISK": ["BAYES", "SPACE"],
        "BIO": ["SPACE", "DATA", "AI"],
    }

    def __init__(
        self,
        suite_manager: Optional[TestSuiteManager] = None,
        dependencies: Optional[Dict[str, List[str]]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.suite_manager = suite_manager or TestSuiteManager()
        self.dependencies = dependencies or dict(self.DEFAULT_DEPENDENCIES)
        self.logger = logger or logging.getLogger(__name__)
        self._execution_log: List[Dict[str, Any]] = []

    def resolve_execution_order(self, modules: List[str]) -> List[str]:
        """
        Topological sort of *modules* respecting their dependency graph.
        Modules not in the graph are appended at the end.
        """
        visited: Set[str] = set()
        order: List[str] = []
        modules_set = set(modules)

        def _visit(m: str) -> None:
            if m in visited:
                return
            visited.add(m)
            for dep in self.dependencies.get(m, []):
                if dep in modules_set:
                    _visit(dep)
            order.append(m)

        for m in modules:
            _visit(m)

        return order

    def plan_execution(
        self,
        suite_name: str = "unit",
        modules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build an execution plan: ordered modules, suite config, and
        estimated duration.
        """
        suite = self.suite_manager.get_suite(suite_name)
        if suite is None:
            raise ValueError(f"Suite '{suite_name}' not found")

        target_modules = modules or suite.modules or list(self.dependencies.keys())
        ordered = self.resolve_execution_order(target_modules)

        plan: Dict[str, Any] = {
            "suite": suite.name,
            "description": suite.description,
            "execution_order": ordered,
            "total_modules": len(ordered),
            "timeout_seconds": suite.timeout_seconds,
            "test_patterns": suite.test_patterns,
            "markers": suite.markers,
        }
        self.logger.info(
            "Execution plan for '%s': %d modules", suite_name, len(ordered)
        )
        return plan

    def execute_plan(
        self,
        plan: Dict[str, Any],
        runner_fn: Optional[Callable[[str], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a plan by calling *runner_fn(module)* for each module
        in order.  Falls back to a no-op if no runner is supplied.
        """
        results: Dict[str, Dict[str, Any]] = {}
        start = time.time()

        for module in plan["execution_order"]:
            mod_start = time.time()
            try:
                if runner_fn:
                    mod_result = runner_fn(module)
                else:
                    mod_result = {"status": "skipped", "reason": "no runner provided"}
                mod_result["duration"] = time.time() - mod_start
                results[module] = mod_result
                self.logger.info(
                    "Module %s: %s (%.2fs)",
                    module, mod_result.get("status", "unknown"), mod_result["duration"],
                )
            except Exception as exc:
                results[module] = {
                    "status": "error",
                    "error": str(exc),
                    "duration": time.time() - mod_start,
                }
                self.logger.error("Module %s failed: %s", module, exc)

        total_duration = time.time() - start
        execution_report = {
            "suite": plan["suite"],
            "module_results": results,
            "total_modules": len(results),
            "total_duration": total_duration,
            "passed": sum(1 for r in results.values() if r.get("status") == "passed"),
            "failed": sum(1 for r in results.values() if r.get("status") in ("failed", "error")),
        }
        self._execution_log.append(execution_report)
        return execution_report

    def get_execution_history(self) -> List[Dict[str, Any]]:
        return list(self._execution_log)
