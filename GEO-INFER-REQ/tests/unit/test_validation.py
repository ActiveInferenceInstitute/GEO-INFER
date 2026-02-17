"""Tests for requirement validation: consistency, conflicts, feasibility."""

import pytest
from geo_infer_req.core.validation import (
    RequirementValidator,
    RequirementSpec,
    ValidationSeverity,
)


@pytest.fixture
def validator():
    v = RequirementValidator()
    v.add_specs([
        RequirementSpec(
            "R1", "Authentication", "Implement OAuth2 authentication with multi-factor",
            priority=4, effort_estimate=10.0,
            tags=["security", "auth", "user"],
            resources_required=["backend_dev"],
        ),
        RequirementSpec(
            "R2", "Data API", "Build REST API for geospatial data management",
            priority=3, effort_estimate=15.0,
            dependencies=["R1"],
            tags=["api", "data"],
            resources_required=["backend_dev"],
        ),
        RequirementSpec(
            "R3", "Frontend", "Build the user interface for the dashboard application",
            priority=2, effort_estimate=20.0,
            dependencies=["R2"],
            tags=["ui", "frontend"],
            resources_required=["frontend_dev"],
        ),
    ])
    return v


class TestRequirementValidator:
    def test_consistency_clean(self, validator):
        report = validator.check_consistency()
        assert report.is_consistent
        assert report.consistency_score > 0.5

    def test_dangling_dependency(self):
        v = RequirementValidator()
        v.add_spec(RequirementSpec(
            "R1", "Req", "A requirement with a valid long description",
            priority=3, effort_estimate=5.0,
            dependencies=["NONEXISTENT"],
        ))
        report = v.check_consistency()
        assert not report.is_consistent
        assert len(report.errors) > 0

    def test_circular_dependency(self):
        v = RequirementValidator()
        v.add_specs([
            RequirementSpec("A", "Req A", "Requirement A has enough description text",
                            priority=3, effort_estimate=5.0, dependencies=["B"]),
            RequirementSpec("B", "Req B", "Requirement B has enough description text",
                            priority=3, effort_estimate=5.0, dependencies=["A"]),
        ])
        report = v.check_consistency()
        assert not report.is_consistent
        assert any("Circular" in e.description for e in report.errors)

    def test_duplicate_titles(self):
        v = RequirementValidator()
        v.add_specs([
            RequirementSpec("R1", "Same Title", "Description one is long enough for validation",
                            priority=3, effort_estimate=5.0),
            RequirementSpec("R2", "Same Title", "Description two is long enough for validation",
                            priority=3, effort_estimate=5.0),
        ])
        report = v.check_consistency()
        assert len(report.warnings) > 0

    def test_short_description_warning(self):
        v = RequirementValidator()
        v.add_spec(RequirementSpec("R1", "Req", "Short", priority=3, effort_estimate=5.0))
        report = v.check_consistency()
        assert any("short description" in w.description for w in report.warnings)

    def test_conflict_detection_constraints(self):
        v = RequirementValidator()
        v.add_specs([
            RequirementSpec("R1", "A", "Description A is sufficiently long for tests",
                            priority=3, effort_estimate=5.0,
                            constraints=["max_memory_512mb", "low_latency"]),
            RequirementSpec("R2", "B", "Description B is sufficiently long for tests",
                            priority=3, effort_estimate=5.0,
                            constraints=["max_memory_512mb", "high_throughput"]),
        ])
        result = v.detect_conflicts()
        assert result.total_conflicts > 0
        assert len(result.conflict_pairs) > 0

    def test_resource_conflict(self):
        v = RequirementValidator()
        v.set_resource_capacity({"backend_dev": 10.0})
        v.add_specs([
            RequirementSpec("R1", "A", "Description A is sufficiently long for tests",
                            priority=3, effort_estimate=8.0,
                            resources_required=["backend_dev"]),
            RequirementSpec("R2", "B", "Description B is sufficiently long for tests",
                            priority=3, effort_estimate=8.0,
                            resources_required=["backend_dev"]),
        ])
        result = v.detect_conflicts()
        assert any(c.severity == ValidationSeverity.ERROR for c in result.conflicts)

    def test_feasibility_within_budget(self, validator):
        result = validator.assess_feasibility(available_effort=100.0)
        assert result.overall_feasibility > 0.0
        assert result.resource_utilization < 1.0
        assert len(result.per_requirement_scores) == 3

    def test_feasibility_over_budget(self, validator):
        result = validator.assess_feasibility(available_effort=10.0)
        assert result.resource_utilization > 1.0
        assert len(result.risk_factors) > 0

    def test_feasibility_no_specs_raises(self):
        v = RequirementValidator()
        with pytest.raises(ValueError, match="No requirement"):
            v.assess_feasibility()

    def test_bottleneck_detection(self):
        v = RequirementValidator()
        v.add_spec(RequirementSpec(
            "R1", "Bottleneck", "This requirement depends on many others heavily",
            priority=3, effort_estimate=5.0,
            dependencies=["A", "B", "C", "D"],
        ))
        v.add_spec(RequirementSpec("A", "A", "Description A is long enough", priority=2, effort_estimate=2.0))
        v.add_spec(RequirementSpec("B", "B", "Description B is long enough", priority=2, effort_estimate=2.0))
        v.add_spec(RequirementSpec("C", "C", "Description C is long enough", priority=2, effort_estimate=2.0))
        v.add_spec(RequirementSpec("D", "D", "Description D is long enough", priority=2, effort_estimate=2.0))
        result = v.assess_feasibility(available_effort=100.0)
        assert "R1" in result.bottleneck_requirements
