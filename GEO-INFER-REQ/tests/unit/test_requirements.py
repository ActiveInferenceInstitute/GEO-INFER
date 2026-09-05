"""Tests for requirements analysis: dependency graphs, priorities, completeness."""

import pytest
from geo_infer_req.core.requirements import (
    RequirementsAnalyzer,
    Requirement,
    RequirementType,
    RequirementStatus,
    PriorityLevel,
)


@pytest.fixture
def analyzer():
    a = RequirementsAnalyzer()
    a.add_requirements([
        Requirement(
            "R001", "User Auth", "Users must authenticate via OAuth2 protocol with MFA support",
            RequirementType.FUNCTIONAL, PriorityLevel.CRITICAL,
            acceptance_criteria=["OAuth2 flow works", "MFA enabled"],
            stakeholders=["security_team", "product"],
            effort_estimate=10.0,
        ),
        Requirement(
            "R002", "Data API", "REST API for CRUD operations on geospatial datasets",
            RequirementType.INTERFACE, PriorityLevel.HIGH,
            dependencies=["R001"],
            acceptance_criteria=["CRUD endpoints work"],
            stakeholders=["engineering"],
            effort_estimate=15.0,
        ),
        Requirement(
            "R003", "Performance", "System must handle 1000 concurrent requests per second",
            RequirementType.PERFORMANCE, PriorityLevel.HIGH,
            dependencies=["R002"],
            acceptance_criteria=["Load test passes"],
            effort_estimate=20.0,
        ),
        Requirement(
            "R004", "Audit Log", "All data modifications must be logged for audit trail compliance",
            RequirementType.SECURITY, PriorityLevel.MEDIUM,
            dependencies=["R001", "R002"],
            acceptance_criteria=["Logs captured"],
            stakeholders=["compliance"],
            effort_estimate=8.0,
        ),
    ])
    return a


class TestRequirementsAnalyzer:
    def test_add_and_retrieve(self, analyzer):
        req = analyzer.get_requirement("R001")
        assert req.title == "User Auth"
        assert req.priority == PriorityLevel.CRITICAL

    def test_duplicate_raises(self, analyzer):
        with pytest.raises(ValueError, match="already exists"):
            analyzer.add_requirement(Requirement("R001", "Dup", "d", RequirementType.FUNCTIONAL))

    def test_not_found_raises(self, analyzer):
        with pytest.raises(KeyError, match="not found"):
            analyzer.get_requirement("R999")

    def test_dependency_graph(self, analyzer):
        graph = analyzer.build_dependency_graph()
        assert len(graph.nodes) == 4
        assert len(graph.edges) > 0
        assert len(graph.cycles) == 0
        # R001 should come before R002 in topological order
        assert graph.topological_order.index("R001") < graph.topological_order.index("R002")

    def test_critical_path(self, analyzer):
        graph = analyzer.build_dependency_graph()
        assert graph.depth >= 2  # R001 -> R002 -> R003
        assert len(graph.critical_path) >= 3

    def test_priority_scores(self, analyzer):
        scores = analyzer.compute_priority_scores()
        assert len(scores) == 4
        # R001 should have high score (critical priority, many dependents)
        assert scores["R001"] > scores["R004"]

    def test_completeness_check(self, analyzer):
        report = analyzer.check_completeness()
        assert report.total_requirements == 4
        assert report.completeness_score > 0.0
        assert len(report.missing_acceptance_criteria) == 0

    def test_incomplete_requirement(self):
        a = RequirementsAnalyzer()
        a.add_requirement(Requirement(
            "R_BAD", "Bad", "short",
            RequirementType.FUNCTIONAL,
        ))
        report = a.check_completeness()
        assert report.completeness_score < 1.0
        assert "R_BAD" in report.missing_descriptions
        assert "R_BAD" in report.missing_acceptance_criteria

    def test_filter_by_type(self, analyzer):
        functional = analyzer.get_requirements_by_type(RequirementType.FUNCTIONAL)
        assert len(functional) == 1
        assert functional[0].req_id == "R001"

    def test_filter_by_status(self, analyzer):
        drafts = analyzer.get_requirements_by_status(RequirementStatus.DRAFT)
        assert len(drafts) == 4

    def test_orphaned_dependencies(self):
        a = RequirementsAnalyzer()
        a.add_requirement(Requirement(
            "R1", "Req", "A requirement that depends on something missing entirely",
            RequirementType.FUNCTIONAL,
            dependencies=["NONEXISTENT"],
        ))
        report = a.check_completeness()
        assert len(report.orphaned_requirements) > 0


class TestCycleDetection:
    """Cycle detection reports well-formed closed loops."""

    def test_two_node_cycle_reconstruction(self):
        a = RequirementsAnalyzer()
        a.add_requirement(Requirement(
            "A", "Req A", "Requirement A depends on requirement B",
            RequirementType.FUNCTIONAL, dependencies=["B"],
        ))
        a.add_requirement(Requirement(
            "B", "Req B", "Requirement B depends back on requirement A",
            RequirementType.FUNCTIONAL, dependencies=["A"],
        ))
        graph = a.build_dependency_graph()
        assert len(graph.cycles) == 1
        cycle = graph.cycles[0]
        # Well-formed: closed loop covering exactly the cycle nodes.
        assert cycle[0] == cycle[-1]
        assert set(cycle[:-1]) == {"A", "B"}

    def test_three_node_cycle_reconstruction(self):
        a = RequirementsAnalyzer()
        a.add_requirements([
            Requirement("A", "RA", "Requirement A depends on B", RequirementType.FUNCTIONAL, dependencies=["B"]),
            Requirement("B", "RB", "Requirement B depends on C", RequirementType.FUNCTIONAL, dependencies=["C"]),
            Requirement("C", "RC", "Requirement C depends back on A", RequirementType.FUNCTIONAL, dependencies=["A"]),
        ])
        graph = a.build_dependency_graph()
        assert len(graph.cycles) == 1
        cycle = graph.cycles[0]
        assert cycle[0] == cycle[-1]
        assert set(cycle[:-1]) == {"A", "B", "C"}
