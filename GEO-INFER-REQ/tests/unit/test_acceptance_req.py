"""
DOMAIN-02 Acceptance tests for GEO-INFER-REQ documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. RequirementsAnalyzer — dependency graph construction, topological order,
   cycle detection, critical path, priority scoring, completeness checking.
2. TraceabilityManager — trace matrix construction, coverage analysis,
   bidirectional links, impact propagation, link verification.
3. RequirementValidator — consistency checking (dangling deps, duplicates),
   conflict detection (overlapping constraints, resource conflicts),
   feasibility assessment with resource utilization.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest

from geo_infer_req.core.requirements import (
    RequirementsAnalyzer,
    Requirement,
    RequirementType,
    RequirementStatus,
    PriorityLevel,
)
from geo_infer_req.core.traceability import (
    TraceabilityManager,
    TraceLink,
    ArtifactType,
)
from geo_infer_req.core.validation import (
    RequirementValidator,
    RequirementSpec,
    ValidationSeverity,
)


# ---------------------------------------------------------------------------
# RequirementsAnalyzer
# ---------------------------------------------------------------------------

class TestRequirementsAnalyzerAcceptance:
    """Acceptance: dependency graph and completeness analysis."""

    @pytest.fixture
    def analyzer(self) -> RequirementsAnalyzer:
        return RequirementsAnalyzer()

    def _chain(self, analyzer):
        """A -> B -> C linear dependency chain (C depends on B depends on A)."""
        analyzer.add_requirements([
            Requirement("A", "Alpha", "Alpha base requirement", RequirementType.FUNCTIONAL),
            Requirement("B", "Beta", "Beta builds on alpha", RequirementType.FUNCTIONAL,
                        dependencies=["A"], acceptance_criteria=["works"]),
            Requirement("C", "Gamma", "Gamma builds on beta", RequirementType.PERFORMANCE,
                        dependencies=["B"], acceptance_criteria=["fast"]),
        ])

    def test_topological_order_respects_dependencies(self, analyzer):
        """A dependency chain yields a topological order with roots first."""
        self._chain(analyzer)
        graph = analyzer.build_dependency_graph()
        assert graph.topological_order.index("A") < graph.topological_order.index("B")
        assert graph.topological_order.index("B") < graph.topological_order.index("C")
        assert graph.cycles == []
        # Critical path traverses the full chain A -> B -> C (depth 2 edges).
        assert graph.depth == 2
        assert graph.critical_path[-1] == "C"

    def test_duplicate_requirement_rejected(self, analyzer):
        """Adding a duplicate req_id raises."""
        analyzer.add_requirement(Requirement("R1", "One", "description text", RequirementType.FUNCTIONAL))
        with pytest.raises(ValueError, match="already exists"):
            analyzer.add_requirement(Requirement("R1", "Dup", "other text", RequirementType.DATA))

    def test_priority_score_higher_for_critical_with_dependents(self, analyzer):
        """A critical requirement that others depend on scores highest."""
        analyzer.add_requirement(Requirement(
            "BASE", "Foundation", "Foundational requirement", RequirementType.FUNCTIONAL,
            priority=PriorityLevel.CRITICAL,
        ))
        analyzer.add_requirement(Requirement(
            "CHILD", "Dependent", "Depends on base", RequirementType.FUNCTIONAL,
            priority=PriorityLevel.LOW, dependencies=["BASE"],
        ))
        scores = analyzer.compute_priority_scores()
        assert scores["BASE"] > scores["CHILD"]

    def test_completeness_flags_missing_criteria_and_orphans(self, analyzer):
        """Incomplete requirements and dangling dependencies are flagged."""
        analyzer.add_requirement(Requirement(
            "R1", "Has all", "A complete description", RequirementType.FUNCTIONAL,
            acceptance_criteria=["criterion one"],
        ))
        analyzer.add_requirement(Requirement(
            "R2", "Missing criteria", "Another full description", RequirementType.DATA,
            dependencies=["NONEXISTENT"],
        ))
        report = analyzer.check_completeness()
        assert report.total_requirements == 2
        assert "R2" in report.missing_acceptance_criteria
        assert any("R2 -> NONEXISTENT" in o for o in report.orphaned_requirements)
        assert report.completeness_score < 1.0

    def test_filter_by_type_and_status(self, analyzer):
        """Filters return only matching requirements."""
        analyzer.add_requirement(Requirement("F1", "F", "functional one", RequirementType.FUNCTIONAL,
                                             status=RequirementStatus.APPROVED))
        analyzer.add_requirement(Requirement("D1", "D", "data one", RequirementType.DATA,
                                             status=RequirementStatus.DRAFT))
        assert len(analyzer.get_requirements_by_type(RequirementType.FUNCTIONAL)) == 1
        assert len(analyzer.get_requirements_by_status(RequirementStatus.APPROVED)) == 1


# ---------------------------------------------------------------------------
# TraceabilityManager
# ---------------------------------------------------------------------------

class TestTraceabilityManagerAcceptance:
    """Acceptance: trace matrix, coverage, and impact analysis."""

    @pytest.fixture
    def manager(self) -> TraceabilityManager:
        return TraceabilityManager()

    def test_coverage_report_counts_traced_and_untraced(self, manager):
        """Requirements with trace links are counted as traced; others are not."""
        manager.register_requirements(["R1", "R2", "R3"])
        manager.add_trace_links([
            TraceLink("R1", "src_a.py", ArtifactType.SOURCE_CODE, verified=True),
            TraceLink("R1", "test_a.py", ArtifactType.TEST_CASE, verified=True),
            TraceLink("R2", "design.md", ArtifactType.DESIGN_DOCUMENT, verified=False),
        ])
        report = manager.analyze_coverage()
        assert report.total_requirements == 3
        assert report.traced_requirements == 2
        assert report.untraced_requirements == ["R3"]
        assert report.coverage_ratio == round(2 / 3, 4)
        assert report.bidirectional_links == 3  # default bidirectional=True

    def test_trace_matrix_verification_status(self, manager):
        """The matrix reflects fully/partially verified states per requirement."""
        manager.register_requirement("R1")
        manager.register_requirement("R2")
        manager.add_trace_link(TraceLink("R1", "a.py", ArtifactType.SOURCE_CODE, verified=True))
        manager.add_trace_link(TraceLink("R1", "b.py", ArtifactType.SOURCE_CODE, verified=True))
        manager.add_trace_link(TraceLink("R2", "c.py", ArtifactType.SOURCE_CODE, verified=False))
        matrix = manager.build_trace_matrix()
        assert matrix["R1"].verification_status == "fully_verified"
        assert matrix["R2"].verification_status == "unverified"
        assert matrix["R1"].forward_coverage == 1.0

    def test_verify_link_flips_status(self, manager):
        """verify_link marks an existing link verified and drops it from unverified."""
        manager.add_trace_link(TraceLink("R1", "a.py", ArtifactType.SOURCE_CODE, verified=False))
        assert manager.verify_link("R1", "a.py") is True
        assert manager.get_unverified_links() == []
        # Verifying a non-existent link returns False.
        assert manager.verify_link("R1", "missing.py") is False

    def test_impact_propagates_through_dependencies(self, manager):
        """Changing a requirement affects its direct artifacts and dependent reqs' artifacts."""
        manager.register_requirement("BASE", dependencies=[])  # root
        manager.register_requirement("CHILD", dependencies=["BASE"])
        manager.add_trace_link(TraceLink("BASE", "base.py", ArtifactType.SOURCE_CODE))
        manager.add_trace_link(TraceLink("CHILD", "child.py", ArtifactType.SOURCE_CODE))
        report = manager.analyze_impact("BASE")
        assert "base.py" in report.directly_affected_artifacts
        assert "CHILD" in report.indirectly_affected_requirements
        assert "child.py" in report.indirectly_affected_artifacts
        assert report.impact_severity > 0.0

    def test_impact_unknown_requirement_raises(self, manager):
        """Analyzing impact for an unregistered requirement raises."""
        with pytest.raises(KeyError, match="not registered"):
            manager.analyze_impact("NOPE")


# ---------------------------------------------------------------------------
# RequirementValidator
# ---------------------------------------------------------------------------

class TestRequirementValidatorAcceptance:
    """Acceptance: consistency, conflict detection, and feasibility."""

    @pytest.fixture
    def validator(self) -> RequirementValidator:
        return RequirementValidator()

    def test_dangling_dependency_is_an_error(self, validator):
        """A dependency on a missing requirement produces an ERROR-level issue."""
        validator.add_spec(RequirementSpec(
            "S1", "Title one", "A complete description", priority=2, effort_estimate=10.0,
            dependencies=["MISSING"],
        ))
        report = validator.check_consistency()
        assert report.is_consistent is False
        assert any(i.severity == ValidationSeverity.ERROR for i in report.errors)
        assert report.consistency_score < 1.0

    def test_clean_spec_set_is_consistent(self, validator):
        """A well-formed spec set has no errors and is reported consistent."""
        validator.add_specs([
            RequirementSpec("S1", "Unique A", "Description one long enough", 2, 10.0),
            RequirementSpec("S2", "Unique B", "Description two long enough", 3, 20.0),
        ])
        report = validator.check_consistency()
        assert report.is_consistent is True
        assert report.errors == []

    def test_overlapping_constraints_detected_as_conflict(self, validator):
        """Two specs sharing a constraint produce an overlapping-conflict warning."""
        validator.add_specs([
            RequirementSpec("S1", "A", "Description one long enough", 2, 10.0,
                            constraints=["must_use_redis"]),
            RequirementSpec("S2", "B", "Description two long enough", 2, 10.0,
                            constraints=["must_use_redis"]),
        ])
        result = validator.detect_conflicts()
        assert result.total_conflicts >= 1
        assert ("S1", "S2") in result.conflict_pairs
        assert result.severity_distribution["warning"] >= 1

    def test_resource_conflict_when_capacity_exceeded(self, validator):
        """Two specs over capacity for a shared resource raise an ERROR conflict."""
        validator.set_resource_capacity({"dev_time": 15.0})
        validator.add_specs([
            RequirementSpec("S1", "A", "Description one long enough", 2, 10.0,
                            resources_required=["dev_time"]),
            RequirementSpec("S2", "B", "Description two long enough", 2, 10.0,
                            resources_required=["dev_time"]),
        ])
        result = validator.detect_conflicts()
        assert result.severity_distribution["error"] >= 1

    def test_feasibility_flags_overcommit(self, validator):
        """Total effort above available effort lowers feasibility and is flagged."""
        validator.add_specs([
            RequirementSpec("S1", "A", "Description one long enough", 4, 60.0),
            RequirementSpec("S2", "B", "Description two long enough", 3, 60.0),
        ])
        assessment = validator.assess_feasibility(available_effort=100.0)
        assert assessment.resource_utilization > 1.0
        assert any("exceeds available" in r for r in assessment.risk_factors)
        assert 0.0 <= assessment.overall_feasibility <= 1.0

    def test_feasibility_empty_raises(self, validator):
        """Assessing feasibility with no specs raises."""
        with pytest.raises(ValueError, match="No requirement specs"):
            validator.assess_feasibility()
