"""Integration tests for GEO-INFER-REQ.

Exercises requirements management end to end: a requirement set is
analysed for dependencies and completeness, then traced to artifacts so
coverage and change impact can be reported.
"""

import pytest

from geo_infer_req import (
    ArtifactType,
    PriorityLevel,
    Requirement,
    RequirementType,
    RequirementsAnalyzer,
    TraceLink,
    TraceabilityManager,
)


@pytest.fixture(name="requirements")
def _requirements():
    """Four requirements forming a small dependency chain."""
    return [
        Requirement(
            req_id="R1",
            title="Ingest sensor readings",
            description="The system ingests readings from field sensors.",
            req_type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            acceptance_criteria=["A reading is persisted within 5s"],
            stakeholders=["operations"],
        ),
        Requirement(
            req_id="R2",
            title="Validate readings",
            description="Readings are quality-checked before storage.",
            req_type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            dependencies=["R1"],
            acceptance_criteria=["Out-of-range readings are flagged"],
            stakeholders=["operations"],
        ),
        Requirement(
            req_id="R3",
            title="Publish a dashboard",
            description="Validated readings are visualised.",
            req_type=RequirementType.INTERFACE,
            priority=PriorityLevel.MEDIUM,
            dependencies=["R2"],
            acceptance_criteria=["The dashboard refreshes every minute"],
            stakeholders=["public"],
        ),
        Requirement(
            req_id="R4",
            title="Encrypt readings at rest",
            description="",
            req_type=RequirementType.SECURITY,
            priority=PriorityLevel.HIGH,
        ),
    ]


@pytest.fixture(name="analyzer")
def _analyzer(requirements):
    analyzer = RequirementsAnalyzer()
    analyzer.add_requirements(requirements)
    return analyzer


@pytest.fixture(name="tracer")
def _tracer(requirements):
    manager = TraceabilityManager()
    for req in requirements:
        manager.register_requirement(req.req_id, dependencies=req.dependencies)
    manager.add_trace_links(
        [
            TraceLink("R1", "ingest.py", ArtifactType.SOURCE_CODE),
            TraceLink("R1", "test_ingest.py", ArtifactType.TEST_CASE, verified=True),
            TraceLink("R2", "validate.py", ArtifactType.SOURCE_CODE),
            TraceLink("R3", "/api/readings", ArtifactType.API_ENDPOINT),
        ]
    )
    return manager


class TestRequirementsAnalysis:
    def test_requirements_are_retrievable_by_id(self, analyzer):
        """A stored requirement comes back intact."""
        assert analyzer.get_requirement("R2").title == "Validate readings"

    def test_requirements_filter_by_type(self, analyzer):
        """Type filtering returns exactly the matching requirements."""
        functional = analyzer.get_requirements_by_type(RequirementType.FUNCTIONAL)
        assert {req.req_id for req in functional} == {"R1", "R2"}

    def test_dependency_graph_orders_the_chain(self, analyzer):
        """Topological order respects R1 -> R2 -> R3."""
        graph = analyzer.build_dependency_graph()
        order = graph.topological_order
        assert order.index("R1") < order.index("R2") < order.index("R3")

    def test_dependency_graph_is_acyclic_here(self, analyzer):
        """A well-formed requirement set reports no cycles."""
        assert analyzer.build_dependency_graph().cycles == []

    def test_a_dependency_cycle_is_detected(self):
        """Mutually dependent requirements are reported, not silently ordered."""
        analyzer = RequirementsAnalyzer()
        analyzer.add_requirements(
            [
                Requirement("A", "A", "a", RequirementType.FUNCTIONAL, dependencies=["B"]),
                Requirement("B", "B", "b", RequirementType.FUNCTIONAL, dependencies=["A"]),
            ]
        )
        assert analyzer.build_dependency_graph().cycles

    def test_completeness_flags_the_incomplete_requirement(self, analyzer):
        """R4 lacks a description and acceptance criteria and is reported."""
        report = analyzer.check_completeness()
        assert report.total_requirements == 4
        assert "R4" in report.missing_descriptions
        assert "R4" in report.missing_acceptance_criteria
        assert 0.0 <= report.completeness_score <= 1.0

    def test_priority_scores_rank_high_above_medium(self, analyzer):
        """A high-priority requirement outscores a medium-priority one."""
        scores = analyzer.compute_priority_scores()
        assert scores["R1"] > scores["R3"]


class TestTraceability:
    def test_coverage_counts_traced_requirements(self, tracer):
        """Three of four requirements have artifacts; R4 has none."""
        report = tracer.analyze_coverage()
        assert report.total_requirements == 4
        assert report.traced_requirements == 3
        assert "R4" in report.untraced_requirements
        assert report.coverage_ratio == pytest.approx(0.75)

    def test_trace_matrix_lists_each_requirement(self, tracer):
        """Every registered requirement appears in the matrix."""
        assert set(tracer.build_trace_matrix()) == {"R1", "R2", "R3", "R4"}

    def test_unverified_links_are_surfaced(self, tracer):
        """Links never verified are reported for follow-up."""
        unverified = tracer.get_unverified_links()
        assert any(link.artifact_id == "validate.py" for link in unverified)
        assert all(link.artifact_id != "test_ingest.py" for link in unverified)

    def test_verifying_a_link_removes_it_from_the_backlog(self, tracer):
        """Verification is recorded and reflected immediately."""
        assert tracer.verify_link("R2", "validate.py") is True
        assert all(link.artifact_id != "validate.py" for link in tracer.get_unverified_links())

    def test_impact_propagates_through_dependents(self, tracer):
        """Changing R1 reaches the requirements built on it."""
        report = tracer.analyze_impact("R1")
        assert report.changed_requirement == "R1"
        assert "ingest.py" in report.directly_affected_artifacts
        assert set(report.indirectly_affected_requirements) >= {"R2"}

    def test_impact_of_a_leaf_requirement_is_contained(self, tracer):
        """A requirement nothing depends on has no downstream requirements."""
        report = tracer.analyze_impact("R3")
        assert report.indirectly_affected_requirements == []
